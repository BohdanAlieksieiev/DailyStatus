# 🔥 DailyStatus

**DailyStatus** is a lightweight desktop application (Tkinter + [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap)) that transforms your Git diffs into a polished daily stand-up report in seconds—powered by Google’s Gemini (Generative Language) API. Ideal for developers, Scrum Masters, and managers looking to automate consistent status updates.

---

## 🎯 Why You Need DailyStatus

- **Fast & Easy**: Gather all commits for a chosen date across selected branches.  
- **One-Click Reports**: Generate **short**, **medium**, or **long** summaries.  
- **AI-Powered**: Leverage Google Gemini to create natural-language stand-up entries.  
- **Local Settings**: All configuration is stored locally—no external telemetry.

---

## 📦 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/DailyStatus.git
   cd DailyStatus

2. **Create & activate a virtual environment (recommended)** 
   ```bash
   python -m venv .venv
   # macOS/Linux:
   source .venv/bin/activate
   # Windows:
   .venv\Scripts\activate

3. **Install dependencies** 
   ```bash
   pip install -r requirements.txt

4. **Run the app** 
   ```bash
   python main.py


## 🔑 How to Get a Free Google Gemini API Key

Before generating reports, you need a free API key from Google AI Studio. Follow these five steps exactly as shown in the screenshots:

1. **Step 1: Login to your Google account**  
   Go to [your Google account](https://www.google.com/) and click **Sign in** in the top-right corner.

2. **Step 2: Visit “Google AI Studio”**  
   Open [https://ai.google.dev/](https://ai.google.dev/)  
   - Click the **Gemini API** tab at the top, or  
   - Click the **Learn more about the Gemini API** button in the center  
   Alternatively, go directly to the Gemini API landing page.  

3. **Step 3: Click “Get API key in Google AI Studio”**  
   On the Gemini API page, find and click the **Get API key in Google AI Studio** button in the center.  

4. **Step 4: Review & approve the Terms of Service**  
   A pop-up will ask you to consent to **Google APIs Terms of Service** and **Gemini API Additional Terms of Service**.  
   - Check the first box (you can also opt in to updates or research invitations)  
   - Click **Continue**  

5. **Step 5: Create your API key**  
   In the next dialog, choose **Create API key in new project** (or select an existing project).  
   Your API key will appear automatically—click **Copy** to save it.  
   <img src="step5.png" alt="Step 5: Create API key" width="600"/>

> **Tip:**  
> • Restrict your key to **Generative Language API** under **API restrictions**.  
> • The free tier provides ample daily quota for stand-up report generation.  


---

## ⚙️ Configuration & Usage

1. **Configure Settings**  
   - On first launch, DailyStatus creates a config file in your home directory:  
     - **Windows:** `%USERPROFILE%\.daily_status_config.json`  
     - **macOS/Linux:** `~/.daily_status_config.json`  
   - Use **Save settings** in the GUI to persist:  
     - Repository folder  
     - Date (YYYY-MM-DD)  
     - Report style  
     - Branches  
     - Gemini API key  
     - Edited prompt template

2. **Generate a Report**  
   - Click **Generate** → diffs are gathered, prompt is built, and AI-generated summary appears.  
   - Copy the output into Slack, Jira, email, or any stand-up tool.

3. **Reset to Defaults**  
   - Delete the config file above and restart DailyStatus to restore initial settings.

---

## 🔒 Privacy & Data Handling

- **Local Processing Only:** We never collect or transmit your code—only the diffs you explicitly send to Gemini API.  
- **No Telemetry:** No usage data or personal information is sent to us.  
- **Config File:** Contains only your paths, date, style, branches, API key, and prompt edits.

---

## ⚖️ License

DailyStatus is licensed under the **MIT License**. See `LICENSE` for full details.