# Master skills database — 250+ skills across all categories

PROGRAMMING_LANGUAGES = [
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
    "perl", "bash", "shell", "powershell", "dart", "lua", "haskell",
    "elixir", "clojure", "groovy", "julia", "fortran", "cobol", "vba"
]

WEB_FRONTEND = [
    "html", "css", "react", "reactjs", "react.js", "angular", "vue", "vuejs",
    "vue.js", "svelte", "nextjs", "next.js", "nuxtjs", "gatsby", "webpack",
    "vite", "tailwind", "tailwindcss", "bootstrap", "sass", "scss", "less",
    "jquery", "redux", "mobx", "graphql", "ajax", "rest", "restful",
    "responsive design", "pwa", "web components", "storybook", "figma",
    "material ui", "chakra ui", "ant design"
]

WEB_BACKEND = [
    "nodejs", "node.js", "express", "expressjs", "django", "flask", "fastapi",
    "spring", "spring boot", "laravel", "rails", "ruby on rails", "asp.net",
    "dotnet", ".net", "nestjs", "fastify", "gin", "fiber", "echo",
    "microservices", "api", "rest api", "graphql api", "grpc", "websocket",
    "oauth", "jwt", "authentication", "authorization"
]

DATABASES = [
    "sql", "mysql", "postgresql", "postgres", "sqlite", "mongodb", "redis",
    "cassandra", "dynamodb", "firebase", "supabase", "oracle", "mssql",
    "sql server", "mariadb", "elasticsearch", "neo4j", "couchdb",
    "influxdb", "prisma", "sqlalchemy", "mongoose", "hibernate",
    "database design", "schema design", "query optimization", "indexing"
]

CLOUD_DEVOPS = [
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker",
    "kubernetes", "k8s", "terraform", "ansible", "jenkins", "github actions",
    "gitlab ci", "circleci", "travis ci", "ci/cd", "devops", "linux",
    "nginx", "apache", "load balancing", "cdn", "serverless", "lambda",
    "ec2", "s3", "rds", "cloudfront", "heroku", "vercel", "netlify",
    "helm", "prometheus", "grafana", "elk stack", "datadog"
]

DATA_SCIENCE_ML = [
    "machine learning", "deep learning", "neural networks", "nlp",
    "natural language processing", "computer vision", "data science",
    "data analysis", "data visualization", "pandas", "numpy", "scipy",
    "matplotlib", "seaborn", "plotly", "scikit-learn", "sklearn",
    "tensorflow", "keras", "pytorch", "hugging face", "transformers",
    "bert", "gpt", "llm", "opencv", "spark", "hadoop", "airflow",
    "mlflow", "feature engineering", "model training", "hyperparameter tuning",
    "random forest", "xgboost", "gradient boosting", "regression",
    "classification", "clustering", "dimensionality reduction", "pca",
    "statistics", "probability", "a/b testing", "hypothesis testing"
]

TOOLS_PLATFORMS = [
    "git", "github", "gitlab", "bitbucket", "jira", "confluence", "slack",
    "trello", "notion", "postman", "swagger", "vs code", "intellij",
    "pycharm", "eclipse", "vim", "linux", "unix", "macos", "windows",
    "excel", "tableau", "power bi", "looker", "jupyter", "colab",
    "anaconda", "virtualenv", "conda", "npm", "yarn", "pip", "maven",
    "gradle", "make", "cmake"
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem solving",
    "critical thinking", "time management", "project management",
    "agile", "scrum", "kanban", "collaboration", "adaptability",
    "creativity", "attention to detail", "analytical skills",
    "presentation", "mentoring", "negotiation", "customer service",
    "stakeholder management", "decision making", "multitasking"
]

CYBERSECURITY = [
    "cybersecurity", "penetration testing", "ethical hacking", "network security",
    "information security", "soc", "siem", "firewall", "vpn", "ssl", "tls",
    "encryption", "cryptography", "vulnerability assessment", "owasp",
    "burp suite", "metasploit", "wireshark", "nmap", "kali linux",
    "incident response", "forensics", "compliance", "gdpr", "iso 27001"
]

MOBILE = [
    "android", "ios", "react native", "flutter", "xamarin", "ionic",
    "swift", "objective-c", "kotlin", "java android", "mobile development",
    "app store", "google play", "firebase", "push notifications"
]

# Combined master list (lowercase, deduplicated)
ALL_SKILLS = list(set(
    PROGRAMMING_LANGUAGES + WEB_FRONTEND + WEB_BACKEND +
    DATABASES + CLOUD_DEVOPS + DATA_SCIENCE_ML +
    TOOLS_PLATFORMS + SOFT_SKILLS + CYBERSECURITY + MOBILE
))

# Category map for classification
SKILL_CATEGORIES = {
    "Software Engineering": PROGRAMMING_LANGUAGES + WEB_FRONTEND + WEB_BACKEND + TOOLS_PLATFORMS,
    "Data Science": DATA_SCIENCE_ML,
    "DevOps / Cloud": CLOUD_DEVOPS,
    "Database": DATABASES,
    "Cybersecurity": CYBERSECURITY,
    "Mobile Development": MOBILE,
}

# Naive Bayes training data (domain → keywords)
NB_TRAINING_DATA = {
    "Software Engineering": [
        "python java javascript react nodejs git api rest docker agile",
        "software developer engineer frontend backend fullstack code",
        "algorithms data structures object oriented programming design patterns",
        "html css typescript vue angular spring microservices ci/cd",
    ],
    "Data Science": [
        "machine learning deep learning neural networks nlp data analysis",
        "pandas numpy scikit-learn tensorflow pytorch jupyter notebook",
        "statistics regression classification clustering feature engineering",
        "data visualization matplotlib seaborn model training evaluation",
    ],
    "Marketing": [
        "seo sem social media marketing content strategy brand management",
        "google analytics facebook ads email marketing campaign roi",
        "copywriting market research consumer behavior digital marketing",
        "hubspot mailchimp crm customer acquisition growth hacking",
    ],
    "Finance": [
        "financial analysis accounting budgeting forecasting excel",
        "risk management investment portfolio valuation dcf modeling",
        "financial reporting audit compliance tax cpa cfa mba",
        "banking trading equity derivatives financial statements",
    ],
    "DevOps / Cloud": [
        "aws azure gcp kubernetes docker terraform ansible jenkins",
        "ci/cd pipeline infrastructure linux server deployment monitoring",
        "cloud architecture serverless microservices scalability reliability",
        "devops sre site reliability engineer automation bash scripting",
    ],
    "Cybersecurity": [
        "penetration testing ethical hacking vulnerability assessment",
        "network security firewall encryption incident response forensics",
        "owasp siem soc security operations compliance gdpr iso",
        "kali linux metasploit burp suite wireshark network protocols",
    ],
}
