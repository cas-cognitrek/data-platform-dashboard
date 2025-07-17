graph TD
    subgraph Data Sources
        RDS[(RDS)]
        S3Raw[(S3 - Raw)]
        Dynamo[(DynamoDB)]
    end

    subgraph Ingestion & Processing
        Glue[AWS Glue Jobs]
        Step[Step Functions]
        DMS[AWS DMS]
    end
    
    subgraph Lakehouse
        S3Lake[(S3 Lake)]
        Athena[Athena]
        Redshift[Redshift]
    end
    
    subgraph Governance (Custom)
        Catalog[Custom Metadata Catalog]
        Lineage[Lineage Engine]
        Glossary[Glossary API]
        UI[Streamlit UI / Custom Portal]
    end
    
    subgraph Security & Control
        LF[AWS Lake Formation]
        IAM[IAM Roles]
    end
    
    subgraph Consumers
        BI[BI Tools / Power BI]
        API[Analytics APIs]
    end
    
    RDS --> DMS --> Glue
    S3Raw --> Glue
    Dynamo --> Glue
    Glue --> S3Lake
    Glue --> Catalog
    Glue --> Lineage
    Catalog --> UI
    Lineage --> UI
    Glossary --> UI
    S3Lake --> Athena --> BI
    S3Lake --> Redshift --> BI
    LF --> Glue
    IAM --> LF
    Catalog --> LF
    UI --> API