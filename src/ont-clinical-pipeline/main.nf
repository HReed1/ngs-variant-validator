nextflow.enable.dsl=2

// Define pipeline parameters
params.run = "RUN-TEST-001" // Default fallback shifted to a Run ID

process FETCH_DB_INPUTS {
    secret 'DB_HOST'
    secret 'DB_USER'
    secret 'DB_PASSWORD'
    secret 'DB_NAME'
    
    input:
    val run_id

    output:
    path "inputs.json", emit: input_json

    script:
    """
    db_fetch_inputs.py --run ${run_id} --out inputs.json
    """
}

process PARSE_INPUTS {
    input:
    path input_json

    output:
    tuple env(RUN_ID), env(READS_URI), env(REF_URI)

    script:
    """
    #!/usr/bin/env python3
    import json
    import os

    with open('${input_json}', 'r') as f:
        data = json.load(f)

    # Export variables so Nextflow can capture them via the env() output declaration
    with open('.command.env', 'w') as env_file:
        env_file.write(f"RUN_ID={data['run_id']}\\n")
        env_file.write(f"READS_URI={data['reads']}\\n")
        env_file.write(f"REF_URI={data['reference']}\\n")
    """
}

process ALIGN_READS {
    input:
    tuple val(run_id), val(reads_uri), val(ref_uri)

    output:
    tuple val(run_id), path("${run_id}.bam"), path("${run_id}.bam.bai"), val(ref_uri), emit: aligned_data

    script:
    """
    # Minimap2 natively supports streaming directly from S3 URIs in many configurations
    minimap2 -ax map-ont ${ref_uri} ${reads_uri} | \\
    samtools sort -o ${run_id}.bam -
    samtools index ${run_id}.bam
    """
}

// Phase 3: Coverage Calculation (mosdepth)
process CALCULATE_COVERAGE {
    input:
    tuple val(run_id), path(bam), path(bai), val(ref_uri)

    output:
    tuple val(run_id), path("${run_id}.mosdepth.global.dist.txt"), path("${run_id}.regions.bed.gz"), emit: coverage_data

    script:
    """
    mosdepth -n --by 500 ${run_id} ${bam}
    """
}

// Phase 4: Variant Calling (Placeholder for Clair3/DeepVariant/GATK)
process CALL_VARIANTS {
    input:
    tuple val(run_id), path(bam), path(bai), val(ref_uri)

    output:
    tuple val(run_id), path("${run_id}.vcf.gz"), emit: raw_vcf

    script:
    """
    # Execute variant caller here
    touch ${run_id}.vcf.gz
    """
}

// Phase 5: Filter by Coverage
process FILTER_BY_COVERAGE {
    input:
    tuple val(run_id), path(vcf), path(mosdepth_bed)

    output:
    tuple val(run_id), path("${run_id}.cov_filtered.vcf"), emit: cov_filtered_vcf

    script:
    """
    filter_by_coverage.py --vcf ${vcf} --bed ${mosdepth_bed} --min_cov 15 --out ${run_id}.cov_filtered.vcf
    """
}

// Phase 6: Clinical Annotation (e.g., VEP or SnpEff)
process ANNOTATE_VARIANTS {
    input:
    tuple val(run_id), path(vcf)

    output:
    tuple val(run_id), path("${run_id}.annotated.vcf"), emit: annotated_vcf

    script:
    """
    # Run annotation tool against dbSNP/gnomAD
    touch ${run_id}.annotated.vcf
    """
}

// Phase 7: Filter Significant Variants & Generate JSON
process GENERATE_JSON_REPORT {
    input:
    tuple val(run_id), path(annotated_vcf)

    output:
    tuple val(run_id), path("${run_id}_clinical_report.json"), emit: json_report

    script:
    """
    generate_json_report.py --vcf ${annotated_vcf} --out ${run_id}_clinical_report.json
    """
}

// Phase 8: Update Database
process LOG_DB_OUTPUTS {
    secret 'DB_HOST'
    secret 'DB_USER'
    secret 'DB_PASSWORD'
    secret 'DB_NAME'
    
    input:
    val run_id
    path clinical_report_json
    path multiqc_metrics_json

    script:
    // Extract the s3 path if staging files remotely, or pass the local/URI string directly
    """
    db_log_outputs.py \\
        --run ${run_id} \\
        --report ${clinical_report_json} \\
        --version "v1.2.0" \\
        --metrics ${multiqc_metrics_json}
    """
}

// Define the Workflow Execution
workflow {
    FETCH_DB_INPUTS(params.run)
    PARSE_INPUTS(FETCH_DB_INPUTS.out.input_json)
    
    ALIGN_READS(PARSE_INPUTS.out)
    
    // Fork the aligned BAM to both coverage and variant calling
    CALCULATE_COVERAGE(ALIGN_READS.out.aligned_data)
    CALL_VARIANTS(ALIGN_READS.out.aligned_data)
    
    // Join the VCF and Coverage data by run_id
    vcf_and_cov = CALL_VARIANTS.out.raw_vcf.join(CALCULATE_COVERAGE.out.coverage_data)
    FILTER_BY_COVERAGE(vcf_and_cov)
    
    ANNOTATE_VARIANTS(FILTER_BY_COVERAGE.out.cov_filtered_vcf)
    GENERATE_JSON_REPORT(ANNOTATE_VARIANTS.out.annotated_vcf)
    
    LOG_DB_OUTPUTS(GENERATE_JSON_REPORT.out.json_report)
}