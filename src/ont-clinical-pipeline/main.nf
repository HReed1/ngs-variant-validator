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
    db_fetch_inputs.py --run ${run_id}
    """
}

process PARSE_INPUTS {
    input:
    path input_json

    output:
    tuple env(RUN_ID), env(READS_URI), env(REF_URI)

    script:
    """
    export RUN_ID=\$(python3 -c "import sys, json; print(json.load(open('${input_json}'))['run_id'])")
    export READS_URI=\$(python3 -c "import sys, json; print(json.load(open('${input_json}'))['reads'])")
    export REF_URI=\$(python3 -c "import sys, json; print(json.load(open('${input_json}'))['reference'])")
    """
}

process ALIGN_READS {
    input:
    tuple val(run_id), val(reads_uri), val(ref_uri)

    output:
    tuple val(run_id), path("${run_id}.bam"), path("${run_id}.bam.bai"), val(ref_uri), emit: aligned_data

    script:
    """
    wget -qO ref.fna.gz "${ref_uri}"
    wget -qO reads.fastq.gz "${reads_uri}"

    minimap2 -ax map-ont ref.fna.gz reads.fastq.gz | \\
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

// Phase 4: Real Variant Calling
process CALL_VARIANTS {
    input:
    tuple val(run_id), path(bam), path(bai), val(ref_uri)

    output:
    tuple val(run_id), path("${run_id}.vcf.gz"), emit: raw_vcf

    script:
    """
    wget -qO ref.fna.gz "${ref_uri}"
    gunzip ref.fna.gz
    # Use bcftools to call variants for the real data
    bcftools mpileup -Ou -f ref.fna ${bam} | bcftools call -mv -Oz -o ${run_id}.vcf.gz
    """
}

// Phase 5: Filter by Quality
process FILTER_BY_COVERAGE {
    input:
    tuple val(run_id), path(vcf), path(mosdepth_dist), path(mosdepth_bed)

    output:
    tuple val(run_id), path("${run_id}.filtered.vcf.gz"), emit: cov_filtered_vcf

    script:
    """
    # Actually filter variants with Quality < 20
    bcftools filter -e 'QUAL<20' ${vcf} -Oz -o ${run_id}.filtered.vcf.gz
    """
}

// Phase 6: Clinical Annotation (Mock pass-through for Micro-Dataset)
process ANNOTATE_VARIANTS {
    input:
    tuple val(run_id), path(vcf)

    output:
    tuple val(run_id), path("${run_id}.annotated.vcf.gz"), emit: annotated_vcf

    script:
    """
    # Rename to simulate annotation step passing
    mv ${vcf} ${run_id}.annotated.vcf.gz
    """
}

// Phase 7: Parse VCF/BED to Generate UI Chart JSON
process GENERATE_JSON_REPORT {
    input:
    // We catch all 4 items from the joined vcf_and_cov channel
    tuple val(run_id), path(annotated_vcf), path(mosdepth_dist), path(mosdepth_bed)

    output:
    tuple val(run_id), path("${run_id}_clinical_report.json"), path("qc_metrics.json"), emit: json_report

    script:
    """
    generate_json_report.py \\
        --vcf ${annotated_vcf} \\
        --bed ${mosdepth_bed} \\
        --out ${run_id}_clinical_report.json \\
        --metrics qc_metrics.json
    """
}

// Phase 8: Update Database
process LOG_DB_OUTPUTS {
    secret 'DB_HOST'
    secret 'DB_PORT'
    secret 'DB_USER'
    secret 'DB_PASSWORD'
    secret 'DB_NAME'
    
    input:
    tuple val(run_id), path(clinical_report_json), path(metrics_json)

    script:
    """
    db_log_outputs.py \\
        --run ${run_id} \\
        --report ${clinical_report_json} \\
        --metrics ${metrics_json} \\
        --version "v1.2.0"
    """
}

// Define the Workflow Execution
workflow {
    FETCH_DB_INPUTS(params.run)
    PARSE_INPUTS(FETCH_DB_INPUTS.out.input_json)
    
    ALIGN_READS(PARSE_INPUTS.out)
    
    CALCULATE_COVERAGE(ALIGN_READS.out.aligned_data)
    CALL_VARIANTS(ALIGN_READS.out.aligned_data)
    
    vcf_and_cov = CALL_VARIANTS.out.raw_vcf.join(CALCULATE_COVERAGE.out.coverage_data)
    FILTER_BY_COVERAGE(vcf_and_cov)
    
    ANNOTATE_VARIANTS(FILTER_BY_COVERAGE.out.cov_filtered_vcf)
    
    // Join the Annotated VCF back with the Mosdepth data so the Python parser can see both!
    annotated_and_cov = ANNOTATE_VARIANTS.out.annotated_vcf.join(CALCULATE_COVERAGE.out.coverage_data)
    
    GENERATE_JSON_REPORT(annotated_and_cov)
    LOG_DB_OUTPUTS(GENERATE_JSON_REPORT.out.json_report)
}