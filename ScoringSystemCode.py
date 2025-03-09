import json

# Load configuration from JSON file
with open('ScoringSystem.json', 'r') as f:
    config = json.load(f)

metric_bounds = config['metric_bounds']
lower_is_better_metrics = config['lower_is_better_metrics']
industry_weights = config['industry_weights']

# Function to normalize numerical metrics to a range of 0 to 1
def normalize_metric(value, min_value, max_value):
    return (value - min_value) / (max_value - min_value) if max_value != min_value else 0.5

# Function to calculate ESG score
def calculate_esg_score(metrics, bounds, lower_is_better_metrics, industry_weights, industry):
    category_scores = {}
    
    # Calculate scores for each category
    for category, subcategories in metrics.items():
        normalized_scores = []
        for metric, value in subcategories.items():
            # Get bounds for the metric
            min_value = bounds[category][metric]['min']
            max_value = bounds[category][metric]['max']
            
            # Normalize the metric
            normalized_score = normalize_metric(value, min_value, max_value)
            
            # Apply 1 - normalized_score if lower is better
            if metric in lower_is_better_metrics:
                normalized_score = 1 - normalized_score
            
            normalized_scores.append(normalized_score)
        
        # Average of normalized scores for the category
        category_scores[category] = sum(normalized_scores) / len(normalized_scores)
    
    # Apply industry-specific weightage
    final_score = (
        category_scores['Environmental'] * industry_weights[industry]['Environmental'] +
        category_scores['Social'] * industry_weights[industry]['Social'] +
        category_scores['Governance'] * industry_weights[industry]['Governance']
    )
    
    # Scale to 10
    return final_score * 10

# Calculate ESG score for a specific industry (e.g., Technology)
industry = 'Technology'
esg_score = calculate_esg_score(extracted_metrics, metric_bounds, lower_is_better_metrics, industry_weights, industry)

# Output result
print(f"ESG Score for {industry} Industry: {esg_score:.2f}/10")
