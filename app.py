import sqlite3
import google.generativeai as genai
from flask import Flask, request, jsonify

# === CONFIGURE GEMINI ===
genai.configure(api_key="your-api-key-here")  # ⬅️ Replace this with your Gemini API key

model = genai.GenerativeModel("gemini-1.5-flash")

DB_PATH = "ecommerce_data.db"

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask_question():
    user_question = request.json.get("question")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    # === Updated Prompt with guidance for all 3 questions ===
    prompt = f"""You are a helpful assistant. Convert the following natural language question into an SQL query.

    The SQLite database has 3 tables:
    1. ad_sales_metrics (columns: item_id, ad_spend, clicks, impressions, ad_sales, units_sold)
    2. total_sales_metrics (columns: item_id, total_sales)
    3. eligibility_table (columns: item_id, is_eligible)

    Guidelines:
    - For "total sales", use: SELECT SUM(total_sales) FROM total_sales_metrics;
    - For RoAS (Return on Ad Spend), calculate: total_sales / ad_spend by joining total_sales_metrics and ad_sales_metrics ON item_id
    - For CPC (Cost Per Click), calculate: ad_spend / clicks from ad_sales_metrics (ensure clicks > 0)
    - Use item_id as the product identifier. Do NOT use product_name (it does not exist).
    - Only return the SQL query. No markdown, no explanation.

    Question: {user_question}
    """

    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip().strip("```sql").strip("```").strip()
    except Exception as e:
        return jsonify({"error": f"Gemini failed: {e}"}), 500

    print("🔍 SQL being executed:\n", sql_query)

    # === Execute the SQL ===
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        result_formatted = [dict(zip(columns, row)) for row in result]
        return jsonify({
            "question": user_question,
            "sql_query": sql_query,
            "result": result_formatted
        })

    except Exception as e:
        return jsonify({"error": f"SQL execution failed: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
