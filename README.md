# 🤖 Azure Cloud RAG Application

**Retrieval-Augmented Generation (RAG) Chatbot built entirely on Azure Cloud.**
This project demonstrates how to combine **Azure OpenAI**, **Cognitive Search**, and **App Service** to create a scalable, secure, and cost-efficient AI solution — ideal for learning Azure and preparing for Solution Engineer roles.

---

## 🌩️ Overview

This application lets users upload documents (PDF, Markdown, or text), automatically indexes them using **Azure Cognitive Search (vector search)**, and enables a chat interface where the **Azure OpenAI Service** provides context-aware answers based on those documents.

It’s fully deployed on Azure using **serverless** and **PaaS** components, with infrastructure managed via **Bicep** and CI/CD automated through **GitHub Actions**.

---

## 🧠 Features

- 📄 Upload and store documents in **Azure Blob Storage**  
- 🔍 Vector + keyword search via **Azure Cognitive Search**  
- 💬 Contextual Q&A powered by **Azure OpenAI Service** (GPT model)  
- 🔐 Secure secrets & access using **Azure Key Vault** + **Managed Identity**  
- ⚙️ Serverless orchestration via **Azure Functions**  
- 🌐 Frontend hosted on **Azure Static Web Apps**  
- 📈 Monitoring with **Application Insights**  
- 🚀 Infrastructure as Code via **Azure Bicep**  
- 🔄 Continuous deployment using **GitHub Actions**

---

## 🧱 Azure Architecture

```

```
      ┌──────────────────────────────┐
      │      Azure Static Web App    │
      │  (React/Vue Frontend)        │
      └──────────────┬───────────────┘
                     │ HTTPS API Calls
                     ▼
             ┌─────────────────────┐
             │   Azure Functions   │
             │  (API Orchestration)│
             └─────────────────────┘
               │       │       │
 ┌─────────────┘       │       └─────────────┐
 ▼                     ▼                     ▼
```

┌──────────────┐    ┌──────────────┐      ┌────────────────┐
│ Azure Blob   │    │ Azure Search │      │ Azure OpenAI   │
│ Storage      │    │ (Vector Index)│     │ (GPT / Embeddings)│
└──────────────┘    └──────────────┘      └────────────────┘
│
▼
┌──────────────┐
│ Azure Key    │
│ Vault + MI   │
└──────────────┘

Logging & Telemetry → Application Insights

````

---

## 🧩 Tech Stack

| Category | Technology | Purpose |
|-----------|----------------|----------|
| Compute / API | **Azure App Service** (Docker container) + **Flask** | Backend REST API |
| Frontend | **Azure Static Web Apps** | Host frontend (HTML/CSS/JavaScript) |
| AI / Search | **Azure OpenAI Service**, **Azure Cognitive Search** | LLM + Vector search |
| Storage | **Azure Blob Storage** | Store uploaded docs |
| Security | **Azure Key Vault**, **Managed Identity**, **Azure AD** | Secrets & authentication |
| Monitoring | **Application Insights**, **Log Analytics** | Telemetry and diagnostics |
| Deployment | **Bicep**, **GitHub Actions**, **Azure Container Registry** | Infrastructure as Code + CI/CD |

---

## 🚀 Quick Start

### 1️⃣ Prerequisites
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Azure Developer Account](https://portal.azure.com/)
- Node.js + npm (for frontend)
- GitHub account (for Actions CI/CD)

### 2️⃣ Deploy Infrastructure
```bash
az login
az group create -n rag-demo-rg -l eastus
az deployment group create -g rag-demo-rg -f infra/main.bicep
````

### 3️⃣ Set Up Local Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/azure-rag-app.git
cd azure-rag-app

# Frontend setup (no dependencies needed - pure HTML/CSS/JS)
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

Set up Azure credentials for local development:

```bash
# Log in to Azure
az login

# Optionally: Set environment variables for non-interactive auth
export AZURE_OPENAI_ENDPOINT=<your-endpoint>
export AZURE_OPENAI_API_KEY=<your-api-key>
export AZURE_SEARCH_ENDPOINT=<your-search-endpoint>
export AZURE_SEARCH_API_KEY=<your-search-api-key>
export AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account>
```

### 5️⃣ Run Locally

```bash
# Terminal 1: Start Flask backend
cd backend
flask run --debug        # Runs on http://localhost:5000

# Terminal 2: Start frontend (from project root)
cd frontend
python -m http.server 8000    # Runs on http://localhost:8000
```

### 6️⃣ Deploy App

Push to `main` — GitHub Actions automatically deploys both the infrastructure and the app.

---

## 📊 Monitoring & Logging

* **Application Insights**: Request logs, exceptions, latency metrics
* **Log Analytics**: Query cross-service telemetry
* **Azure Cost Management**: Budget alerts to stay within free credits

Example KQL query for Function metrics:

```kql
requests
| where cloud_RoleName == "rag-functions"
| summarize avg(duration), count() by operation_Name
```

---

## 💰 Cost Optimization Tips

| Resource         | Strategy                                 |
| ---------------- | ---------------------------------------- |
| Azure OpenAI     | Limit max tokens, cache responses        |
| Cognitive Search | Start with **Free** or **S1 Small** tier |
| Blob Storage     | Delete unused blobs                      |
| Functions        | Use **Consumption Plan** (pay per use)   |
| Static Web App   | Free tier is sufficient                  |
| App Insights     | Retain logs only 7 days for dev          |

---

## 🧭 Future Improvements

* Chat history with **Cosmos DB**
* User authentication with **Azure AD B2C**
* Re-indexing pipeline via **Event Grid**
* Custom analytics dashboard (Power BI Embedded)
* Multi-region deployment (Front Door)

---

## 🎓 Learning Outcomes

✅ Understanding of Azure PaaS & Serverless architecture
✅ Practical experience with Cognitive Search + OpenAI integration
✅ Hands-on with Key Vault, Managed Identity, App Insights, and IaC
✅ End-to-end CI/CD deployment and cost management

---

## 🧑‍💻 Author

**Linus Stuhlmann**
Cloud & AI Enthusiast | Azure Solution Engineer in Training
🌐 [https://www.linkedin.com/in/linus-stuhlmann-29b3831ba](https://www.linkedin.com/in/linus-stuhlmann-29b3831ba)

---

## 📜 License

MIT License – free to use, learn, and build upon.