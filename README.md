# 🛡️ TrustTrace AI

**TrustTrace AI** is an autonomous multi-agent fraud detection system that analyzes suspicious messages such as scam SMS, phishing emails, fake UPI requests, lottery scams, and fraudulent job offers.

Built for the **ET Hackathon 2026**, this project demonstrates how **Agentic AI** can be applied to a real-world enterprise workflow by autonomously detecting risk, retrieving supporting evidence, making decisions, suggesting actions, and maintaining an auditable trail.

---

## 🚀 Problem It Solves

Digital fraud messages often create urgency, impersonate trusted institutions, and manipulate users into sharing sensitive information or making payments.

Most users struggle to answer questions like:
- Is this message a scam?
- Why is it suspicious?
- What should I do next?
- Has a similar fraud case happened before?

**TrustTrace AI** solves this by converting fraud analysis into a **multi-step autonomous AI workflow**.

---

## 🎯 Hackathon Problem Statement Fit

This project maps to the ET Hackathon track:

### **Agentic AI for Autonomous Enterprise Workflows**

Why it fits:
- Uses a **multi-agent workflow**
- Executes a **complex multi-step process**
- Performs **autonomous decision-making**
- Includes **retry/error handling**
- Maintains an **audit trail for explainability**

Instead of simply classifying a message, the system takes ownership of the full fraud assessment workflow.

---

## ✨ Key Features

- **Multi-Agent Architecture**
  - Detection Agent
  - Retrieval Agent
  - Analysis Agent
  - Decision Agent
  - Action Agent
  - Audit Agent

- **Fraud Message Analysis**
  - Detects scam-like patterns in suspicious messages

- **RAG-style Similar Case Retrieval**
  - Retrieves similar fraud cases for better context and justification

- **Risk Classification**
  - Classifies messages into **Low / Medium / High Risk**

- **Scam Indicator Detection**
  - Urgency
  - Impersonation
  - Suspicious links
  - Financial manipulation
  - Social engineering cues

- **Suggested Actions**
  - Recommends what the user should do next

- **Complaint Draft Generation**
  - Helps users report suspicious fraud cases

- **Auditability**
  - Stores a complete workflow reasoning trail

- **Retry Logic / Workflow Resilience**
  - Handles transient LLM/API failures more gracefully

---

## 🧠 How It Works

The system processes a suspicious message through a sequence of specialized AI agents:

### 1. Detection Agent
Identifies whether the input message contains scam or fraud-like signals.

### 2. Retrieval Agent
Fetches similar fraud cases from a fraud knowledge base to provide supporting context.

### 3. Analysis Agent
Examines deeper scam indicators such as urgency, impersonation, suspicious links, and malicious intent.

### 4. Decision Agent
Assigns the final risk category and generates the final justification.

### 5. Action Agent
Suggests safe next steps for the user and optionally generates a complaint/report draft.

### 6. Audit Agent
Stores a transparent audit trail of decisions for explainability and enterprise trust.

---

## 🏗️ System Architecture

```text
User Input Message
        ↓
Detection Agent
        ↓
Retrieval Agent (RAG)
        ↓
Analysis Agent
        ↓
Decision Agent
        ↓
Action Agent
        ↓
Audit Agent
        ↓
Dashboard Output
```

---

## 🖥️ User Interface

The Streamlit dashboard allows users to:

- Paste suspicious SMS / Email / UPI / Scam content
- Run AI-based fraud analysis
- View:
  - Classification
  - Confidence
  - Safety Score
  - Scam Indicators
  - Similar Fraud Cases
  - Suggested Actions
  - Audit Trail
  - Complaint Draft

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit**

### Backend
- **Python**

### AI / LLM
- **Google Gemini API**

### Workflow / Logic
- Multi-agent orchestration
- JSON-structured LLM outputs
- Retry and escalation logic

### Retrieval
- Fraud case retrieval / RAG-style context matching

---

## 📂 Project Structure

```bash
TrustTrace-AI/
│
├── app.py                  # Main Streamlit app
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
│
├── utils/
│   ├── orchestrator.py     # End-to-end workflow orchestration
│   ├── llm.py              # Gemini LLM service
│   ├── ...                 # Agent logic / helper modules
│
└── data/
    └── ...                 # Fraud cases / retrieval context (if used)
```

> Update this section if your actual folder structure is slightly different.

---

## ⚙️ Setup Instructions

### 1) Clone the repository
```bash
git clone <your-repo-url>
cd TrustTrace-AI
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Set your Gemini API key

#### Windows (Command Prompt)
```bash
set GEMINI_API_KEY=your_api_key
```

#### Windows (PowerShell)
```bash
$env:GEMINI_API_KEY="your_api_key"
```

#### Linux / Mac
```bash
export GEMINI_API_KEY="your_api_key"
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

Then open the local Streamlit URL in your browser.

---

## 🧪 Sample Test Messages

You can test the app using examples like:

### High-Risk KYC Scam
```text
Dear customer, your KYC is pending. Your account will be blocked in 2 hours. Verify now: http://secure-kyc-update.in
```

### Fake UPI Collect Scam
```text
You have received a collect request of Rs 25,000 from SBI Rewards. Approve UPI PIN immediately to claim cashback.
```

### Lottery Scam
```text
Congratulations! You won Rs 12,50,000 in the National Lucky Draw. Pay processing fee today to release funds.
```

### Fake Job Offer
```text
We are hiring for remote data entry with Rs 45,000 salary. Pay Rs 1,999 registration to confirm your seat.
```

### Safer Example
```text
Your transaction of Rs 1,250 on card ending 4482 was successful. If not you, call official helpline on bank website.
```

---

## 📌 Example Output

For each message, TrustTrace AI can generate:

- **Final Risk Category**
- **Confidence Score**
- **Safety Score**
- **Scam Indicators**
- **Retrieved Similar Fraud Cases**
- **Recommended User Actions**
- **Complaint Draft**
- **Audit Trail**

---

## 🔍 Why This Project Matters

Fraud detection is not only a cybersecurity problem — it is also a **workflow automation** problem.

TrustTrace AI demonstrates how agentic systems can:
- detect harmful content,
- reason through uncertainty,
- retrieve supporting evidence,
- explain decisions,
- and recommend action

…all while preserving **transparency and auditability**.

This makes it relevant for:
- Banks
- Fintech platforms
- Telecom providers
- Customer support systems
- Enterprise security workflows

---

## ⚠️ Current Limitations

- Prototype-level knowledge base
- Primarily focused on text-based fraud messages
- No live URL/domain reputation scoring yet
- Output quality depends on prompt engineering and LLM consistency

---

## 🔮 Future Improvements

- Multilingual scam detection
- OCR for screenshot-based scam messages
- URL/domain reputation checks
- WhatsApp / Email integration
- Live fraud reporting integrations
- Stronger retrieval pipeline with vector database
- Admin dashboard for enterprise monitoring

---

## 👥 Team / Submission Note

Built as a hackathon prototype for **ET Hackathon 2026**.

---

## 📜 License
MIT License — This project is for educational / prototype / hackathon demonstration purposes.