# AWS Setup & Handoff Guide

**Project:** LoopBack
**Purpose:** Instructions for configuring Amazon Bedrock as an optional LLM provider for the LoopBack investigation agent.

---

## A. AWS Account Setup

The AWS account owner must complete these steps before the backend can use Amazon Bedrock:

1. **Select a Region:** Choose an AWS region where Amazon Bedrock is supported (e.g., `us-east-1` or `us-west-2`).
2. **Request Model Access:**
   - Go to the **Amazon Bedrock** console in your selected region.
   - Click on **Model access** in the left sidebar.
   - Click **Manage model access** and check the box for **Meta Llama 3 8B Instruct** (or equivalent 70B model).
   - Submit the request. Access is usually granted within minutes.
3. **Verify Pricing:** Check the Bedrock pricing page for Llama 3 models. Usage is billed per token. If you have AWS Activate credits, ensure they are applied to your account.
4. **Create IAM Permissions:**
   - Create an IAM User (or Role for EC2/ECS if deploying).
   - Attach a policy granting `bedrock:InvokeModel` on the specific model ARN. 
   - *Example Policy:*
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Effect": "Allow",
           "Action": "bedrock:InvokeModel",
           "Resource": "arn:aws:bedrock:*::foundation-model/meta.llama3-8b-instruct-v1:0"
         }
       ]
     }
     ```
5. **Generate Credentials:** Generate an Access Key and Secret Access Key for this IAM User. **Do not share the Secret Access Key over chat.** Provide them securely or configure them directly on the machine running the backend.

---

## B. Configuration Variables

The application uses standard `.env` variables located in the backend directory. 

| Variable Name | Purpose | Location | Supplied By | Secret? | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `LLM_PROVIDER` | Determines whether to use local Ollama or AWS Bedrock | `backend/.env` | Developer | No | `bedrock` |
| `AWS_REGION` | The region where Bedrock is active | `backend/.env` | AWS Owner | No | `us-east-1` |
| `BEDROCK_MODEL_ID` | The exact Bedrock model string | `backend/.env` | AWS Owner | No | `meta.llama3-8b-instruct-v1:0` |
| `AWS_PROFILE` | Named AWS CLI profile to use (optional) | `backend/.env` | AWS Owner | No | `default` |
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key | `backend/.env` | AWS Owner | **YES** | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY`| AWS IAM Secret Key | `backend/.env` | AWS Owner | **YES** | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |

**Security Warning:**
- The exact local file path is `backend/.env`.
- Do NOT commit `backend/.env` to Git. (It is correctly listed in `.gitignore`).
- A safe placeholder file exists at `backend/.env.example`.
- Never place AWS credentials in `frontend/.env` or React code, as that exposes them to browser clients.

---

## C. Responsibilities

**Teammate's Tasks (AWS Owner):**
1. Log into the AWS Console, select a region, and enable access to Meta Llama 3 in Bedrock.
2. Create an IAM User with `bedrock:InvokeModel` permissions and generate Access Keys.
3. Configure the keys locally on the machine running the backend. You can either use `aws configure` to set up an AWS CLI profile, or paste the keys into the `backend/.env` file.
4. Verify there are no unexpected charges on the billing dashboard.

**My Tasks (Developer):**
1. I have updated the backend to dynamically route requests to `boto3` when `LLM_PROVIDER=bedrock`.
2. I have added automated mock tests to verify Bedrock branching without incurring charges.
3. I will test the live API locally once you configure the credentials.

---

## D. Verification Checklist

Run these commands in Windows PowerShell to verify the integration.

**1. Verify AWS CLI (Local Identity Test):**
```powershell
aws sts get-caller-identity
```
*(This confirms credentials are active without printing the secret key.)*

**2. Start the Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**3. Start the Frontend:**
```powershell
cd frontend
npm run dev
```

**4. Trigger an Investigation (Live Test):**
1. Open the React frontend at `http://localhost:5173`.
2. Click on an incident and click **Investigate**.
3. *Verification:* If Bedrock runs successfully, the frontend Agent Panel will display **Investigation complete [Amazon Bedrock (Llama 3)]**.

**5. Run Automated Tests (Local Only / No AWS Charges):**
```powershell
cd backend
.\venv\Scripts\pytest tests -v
```
*(Tests include `test_mocked_bedrock_successful_llm_json` which mocks the `boto3` client).*

---

## E. Troubleshooting

- **`AccessDeniedException` or `UnrecognizedClientException`**: The AWS credentials in `.env` are missing, invalid, or the IAM user lacks the `bedrock:InvokeModel` permission.
- **`ValidationException` (Model not available)**: The model you specified in `BEDROCK_MODEL_ID` hasn't been enabled in the Bedrock console, or you are targeting a region where it isn't supported.
- **Fallback Behavior**: If Bedrock times out or throws an error, the backend safely catches the exception and falls back to the `Deterministic Rules Engine`. The `used_llm` flag will be `False`. If you prefer to fall back to `ollama`, simply change `LLM_PROVIDER=ollama` in `.env`.

---

## F. Security & Handoff Checklist

- [x] No AWS credentials are committed to Git.
- [x] `backend/.env` is ignored in `.gitignore`.
- [x] `backend/.env.example` contains placeholders only.
- [x] No secrets have been transmitted over chat.
- [x] The application continues to work entirely locally (using Ollama) if `LLM_PROVIDER` is unset or set to `ollama`.
