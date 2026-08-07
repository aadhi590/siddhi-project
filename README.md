# 🍽️ Restaurant Lead Finder AI

This application helps you discover newly opened restaurants in Chennai and identifies which ones are the best candidates for marketing collaborations.

The system automatically:

✅ Finds new restaurants

✅ Scans selected Chennai areas

✅ Analyzes restaurant photos

✅ Uses AI to understand the restaurant

✅ Calculates collaboration opportunities

✅ Generates personalized outreach messages

---

# 📋 Before You Start

You only need the following:

- Windows Laptop
- Internet Connection
- Python installed
- PostgreSQL installed
- Google Places API Key
- Google Vision API Key
- Gemini API Key (or OpenAI API Key)

---

# 📥 Step 1 - Download the Project

If you received this project as a ZIP file:

Extract it anywhere.

Example:

```
C:\RestaurantLeadFinder
```

If you received a GitHub link:

Open Command Prompt and run

```bash
git clone YOUR_GITHUB_REPOSITORY
```

Then enter the project folder.

```bash
cd restaurant-lead-finder-ai/backend
```

---

# 🐍 Step 2 - Create Python Environment

Run:

```bash
python -m venv .venv
```

Activate it.

Windows

```bash
.venv\Scripts\activate
```

You should now see

```
(.venv)
```

at the beginning of the terminal.

---

# 📦 Step 3 - Install Required Packages

Run

```bash
pip install -r requirements.txt
```

Wait until everything finishes installing.

---

# 🗄️ Step 4 - Setup PostgreSQL

Create a database.

Example database name

```
restaurant_ai
```

Remember

- Database Name
- Username
- Password

You will need these in the next step.

---

# 🔑 Step 5 - Configure API Keys

Inside the project folder you will find

```
.env.example
```

Rename it to

```
.env
```

Open it using Notepad.

Fill the following values.

Example

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/restaurant_ai

GOOGLE_PLACES_API_KEY=YOUR_GOOGLE_PLACES_API_KEY

GOOGLE_VISION_API_KEY=YOUR_GOOGLE_VISION_API_KEY

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

OPENAI_API_KEY=

LLM_PROVIDER=gemini
```

Save the file.

---

# 🛠️ Step 6 - Create Database Tables

Run

```bash
alembic upgrade head
```

This only needs to be done once.

---

# ▶️ Step 7 - Start the Application

Run

```bash
uvicorn app.main:app --reload
```

If everything is correct you will see

```
Application started successfully
```

---

# 🌐 Step 8 - Open the Application

Open your browser.

Go to

```
http://127.0.0.1:8000/docs
```

This page contains all the available features.

---

# 🚀 Main Features

## Scan Entire Chennai

This scans all configured Chennai areas.

```
POST /api/v1/scan/chennai
```

---

## Scan Saved Areas

If you have saved watch areas

```
POST /api/v1/scan/watchlist
```

---

## View Today's Best Leads

```
GET /api/v1/leads/today
```

Shows

- Newly discovered restaurants
- Opportunity Score
- Marketing Readiness
- AI Summary
- Contact Details
- Outreach Message

---

## Daily Report

```
GET /api/v1/reports/daily-sales-report
```

Shows

- Restaurants found today
- New restaurants
- Opening soon
- Best collaboration opportunities

---

## Restaurant Details

```
GET /api/v1/restaurants
```

Shows every restaurant stored in the database.

---

## AI Analysis

```
POST /api/v1/restaurants/analyze/{restaurant_id}
```

The AI will generate

- Restaurant Type
- Target Audience
- Marketing Readiness
- Opportunity Score
- Business Summary

---

## AI Outreach

```
POST /api/v1/restaurants/outreach/{restaurant_id}
```

Automatically creates

- Email
- WhatsApp Message
- Instagram Message

---

# 📊 What the Scores Mean

### Opportunity Score

Higher score = Better collaboration opportunity.

Example

```
95
```

Excellent lead.

Contact immediately.

---

### Marketing Readiness

Shows how likely the restaurant is to need marketing.

Higher score = Higher chance of becoming a client.

---

### New Restaurant Score

Shows how confident the AI is that the restaurant is newly opened.

---

# ❓Common Problems

## "API Key Missing"

Check the

```
.env
```

file.

Make sure every API key is filled correctly.

---

## Database Error

Make sure PostgreSQL is running.

---

## Port Already in Use

Run

```bash
uvicorn app.main:app --reload --port 8001
```

---

# 📞 Need Help?

If something doesn't work

1. Take a screenshot of the error.
2. Send the screenshot.
3. Mention which step you were following.

This helps identify the problem quickly.

---

# 🎯 Daily Usage

Every morning:

1. Start the application.
2. Open

```
http://127.0.0.1:8000/docs
```

3. Run

```
POST /api/v1/scan/chennai
```

4. Wait for the scan to complete.

5. Open

```
GET /api/v1/leads/today
```

6. Contact the top restaurants shown by the AI.

That's it.
