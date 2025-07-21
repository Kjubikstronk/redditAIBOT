from flask import Flask, render_template, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

# Enhanced mock data generation functions
def generate_mock_comment():
    authors = [
        'tech_enthusiast_42', 'ai_researcher', 'curious_user', 'data_scientist', 
        'ml_student', 'ethics_advocate', 'nlp_specialist', 'future_coder',
        'ai_skeptic', 'innovation_lover'
    ]
    
    subreddits = [
        'artificial', 'MachineLearning', 'ChatGPT', 'OpenAI', 'technology', 
        'programming', 'datascience', 'ArtificialIntelligence', 'singularity',
        'futurology'
    ]
    
    verdicts = ['🔴 Potentially AI-Generated', '🟡 Possibly AI-Generated', '🟢 Likely Human']
    
    # More realistic comment templates
    comment_templates = [
        "This is a fascinating discussion about artificial intelligence and its impact on society. The implications are far-reaching and deserve careful consideration.",
        "Machine learning algorithms have revolutionized data analysis in recent years. The advancement in neural networks is particularly impressive.",
        "Has anyone tried the new ChatGPT update? The responses seem more natural now, though I'm still evaluating its reliability for complex tasks.",
        "The implementation of neural networks in various domains has shown remarkable results in pattern recognition and predictive modeling.",
        "I'm working on a project that involves natural language processing and sentiment analysis. The results have been quite promising so far.",
        "The ethical implications of AI development need to be carefully considered as we move forward with these powerful technologies.",
        "Natural language processing has made significant strides recently. The ability to understand context and nuance is improving rapidly.",
        "I've been experimenting with different AI models for text generation, and the quality has improved dramatically over the past year.",
        "The debate around AI consciousness is fascinating. While we're not there yet, the philosophical questions are worth exploring.",
        "Machine learning bias is a critical issue that needs more attention. We must ensure our models are fair and representative."
    ]
    
    # Add some variation to make comments more realistic
    base_comment = random.choice(comment_templates)
    extensions = [
        " What are your thoughts on this?",
        " I'd love to hear other perspectives.",
        " Has anyone else noticed similar trends?",
        " This could have significant implications for the future.",
        " I'm curious about the long-term effects.",
        " The research in this area is evolving rapidly.",
        " We should be cautious but optimistic about these developments.",
        " The potential applications are endless.",
        " This raises important questions about regulation.",
        " I think we're just scratching the surface here."
    ]
    
    full_comment = base_comment + random.choice(extensions)
    
    return {
        'id': str(random.randint(1000, 9999)),
        'content': full_comment,
        'author': random.choice(authors),
        'subreddit': random.choice(subreddits),
        'timestamp': f"{random.randint(1, 24)} hours ago",
        'verdict': random.choice(verdicts),
        'confidence': random.randint(60, 95),
        'permalink': f'/r/{random.choice(subreddits)}/comments/example{random.randint(1, 1000)}',
        'upvotes': random.randint(5, 100),
        'downvotes': random.randint(0, 20),
    }

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    # Generate more realistic mock data
    recent_triggers = [generate_mock_comment() for _ in range(8)]
    
    # More realistic distribution
    ai_generated = random.randint(120, 180)
    possibly_ai = random.randint(60, 120)
    likely_human = random.randint(200, 350)
    
    verdict_distribution = {
        '🔴 Potentially AI-Generated': ai_generated,
        '🟡 Possibly AI-Generated': possibly_ai,
        '🟢 Likely Human': likely_human,
    }
    
    subreddit_activity = {
        'artificial': random.randint(30, 60),
        'MachineLearning': random.randint(25, 55),
        'ChatGPT': random.randint(20, 50),
        'OpenAI': random.randint(15, 45),
        'technology': random.randint(18, 40),
        'programming': random.randint(10, 35),
        'datascience': random.randint(12, 30),
        'ArtificialIntelligence': random.randint(8, 25),
        'singularity': random.randint(5, 20),
        'futurology': random.randint(6, 22),
    }
    
    # Generate trend data for the past week
    trend_labels = [(datetime.now() - timedelta(days=i)).strftime('%m/%d') for i in range(6, -1, -1)]
    
    return jsonify({
        'total_triggers': sum(verdict_distribution.values()) + random.randint(800, 1500),
        'verdict_distribution': verdict_distribution,
        'recent_triggers': recent_triggers,
        'subreddit_activity': subreddit_activity,
        'verdict_trends': {
            'labels': trend_labels,
            'datasets': {
                '🔴 Potentially AI-Generated': [random.randint(15, 35) for _ in range(7)],
                '🟡 Possibly AI-Generated': [random.randint(8, 25) for _ in range(7)],
                '🟢 Likely Human': [random.randint(25, 50) for _ in range(7)],
            }
        }
    })

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
