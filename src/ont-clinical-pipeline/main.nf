nextflow.enable.dsl=2

// Define pipeline parameters
params.sample = "SRR11032656" // Default fallback

process FETCH_DB_INPUTS {
    secret 'DB_HOST'
    secret 'DB_USER'
    secret 'DB_PASSWORD'
    secret 'DB_NAME'
    
    input:
    val sample_id

    output:
    path "inputs.json", emit: input_json

    script:
    """
    db_fetch_inputs.py --sample ${sample_id} --out inputs.json
    """
}

process PARSE_INPUTS {
    input:
    path input_json

    output:
    tuple env(SAMPLE_ID), env(READS_URI), env(REF_URI)

    script:
    """
    #!/usr/bin/env python3
    import json
    import os

    with open('${input_json}', 'r') as f:
        data = json.load(f)

    # Export variables so Nextflow can capture them via the env() output declaration
    with open('.command.env', 'w') as env_file:
        env_file.write(f"SAMPLE_ID={data['sample_id']}\\n")
        env_file.write(f"READS_URI={data['reads']}\\n")
        env_file.write(f"REF_URI={data['reference']}\\n")
    """
}

process ALIGN_READS {
    input:
    tuple val(sample_id), val(reads_uri), val(ref_uri)

    output:
    tuple val(sample_id), path("${sample_id}.bam"), path("${sample_id}.bam.bai"), val(ref_uri), emit: aligned_data

    script:
    """
    # Minimap2 natively supports streaming directly from S3 URIs in many configurations
    minimap2 -ax map-ont ${ref_uri} ${reads_uri} | samtools sort -o ${sample_id}.bam -
    samtools index ${sample_id}.bam
    """
}

// Phase 3: Coverage Calculation (mosdepth)
process CALCULATE_COVERAGE {
    input:
    tuple val(sample_id), path(bam), path(bai), val(ref_uri)

    output:
    tuple val(sample_id), path("${sample_id}.mosdepth.global.dist.txt"), path("${sample_id}.regions.bed.gz"), emit: coverage_data

    script:
    """
    mosdepth -n --by 500 ${sample_id} ${bam}
    """
}

// Phase 4: Variant Calling (Placeholder for Clair3/DeepVariant/GATK)
process CALL_VARIANTS {
    input:
    tuple val(sample_id), path(bam), path(bai), val(ref_uri)

    output:
    tuple val(sample_id), path("${sample_id}.vcf.gz"), emit: raw_vcf

    script:
    """
    # Execute variant caller here
    touch ${sample_id}.vcf.gz
    """
}

// Phase 5: Filter by Coverage
process FILTER_BY_COVERAGE {
    input:
    tuple val(sample_id), path(vcf), path(mosdepth_bed)

    output:
    tuple val(sample_id), path("${sample_id}.cov_filtered.vcf"), emit: cov_filtered_vcf

    script:
    """
    filter_by_coverage.py --vcf ${vcf} --bed ${mosdepth_bed} --min_cov 15 --out ${sample_id}.cov_filtered.vcf
    """
}

// Phase 6: Clinical Annotation (e.g., VEP or SnpEff)
process ANNOTATE_VARIANTS {
    input:
    tuple val(sample_id), path(vcf)

    output:
    tuple val(sample_id), path("${sample_id}.annotated.vcf"), emit: annotated_vcf

    script:
    """
    # Run annotation tool against dbSNP/gnomAD
    touch ${sample_id}.annotated.vcf
    """
}

// Phase 7: Filter Significant Variants & Generate JSON
process GENERATE_JSON_REPORT {
    input:
    tuple val(sample_id), path(annotated_vcf)

    output:
    tuple val(sample_id), path("${sample_id}_clinical_report.json"), emit: json_report

    script:
    """
    generate_json_report.py --vcf ${annotated_vcf} --out ${sample_id}_clinical_report.json
    """
}

// Phase 8: Update Database
process LOG_DB_OUTPUTS {
    input:
    tuple val(sample_id), path(json_report)

    script:
    """
    db_log_outputs.py --sample ${sample_id} --report_path \$(realpath ${json_report})
    """
}

// Define the Workflow Execution
workflow {
    FETCH_DB_INPUTS(params.sample)
    PARSE_INPUTS(FETCH_DB_INPUTS.out.input_json)
    
    ALIGN_READS(PARSE_INPUTS.out)
    
    // Fork the aligned BAM to both coverage and variant calling
    CALCULATE_COVERAGE(ALIGN_READS.out.aligned_data)
    CALL_VARIANTS(ALIGN_READS.out.aligned_data)
    
    // Join the VCF and Coverage data by sample_id
    vcf_and_cov = CALL_VARIANTS.out.raw_vcf.join(CALCULATE_COVERAGE.out.coverage_data)
    FILTER_BY_COVERAGE(vcf_and_cov)
    
    ANNOTATE_VARIANTS(FILTER_BY_COVERAGE.out.cov_filtered_vcf)
    GENERATE_JSON_REPORT(ANNOTATE_VARIANTS.out.annotated_vcf)
    
    LOG_DB_OUTPUTS(GENERATE_JSON_REPORT.out.json_report)
}