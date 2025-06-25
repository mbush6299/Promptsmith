"""
Chart Builder Agent

This agent takes a visualization prompt and generates a Vega-Lite chart specification.

Input: prompt (string)
Output: chart_spec (JSON string) - Vega-Lite format
"""

from typing import Dict, Any, Optional
import json
import random
from llm_utils import chat_completion
from learning_cache import learning_cache


class ChartBuilderAgent:
    """Agent responsible for building chart specifications from prompts."""
    
    def __init__(self):
        self.name = "chart_builder"
        self.description = "Generates Vega-Lite chart specifications from visualization prompts"
    
    def build_chart(self, prompt: str, user_query: str = "") -> Dict[str, Any]:
        """
        Build a chart specification from a prompt.
        
        Args:
            prompt (str): Visualization prompt
            user_query (str): Original user query for cache lookup
            
        Returns:
            Dict[str, Any]: Chart specification and metadata
        """
        # Only use cache for exact matches to avoid generating identical charts
        if user_query:
            cached_chart_spec = learning_cache.suggest_chart_spec(user_query)
            if cached_chart_spec:
                # Only use cache for exact matches
                query_hash = learning_cache._hash_query(user_query)
                if query_hash in learning_cache.patterns["query_patterns"]:
                    cached_query = learning_cache.patterns["query_patterns"][query_hash]["query"]
                    if user_query.lower().strip() == cached_query.lower().strip():
                        print(f"🎯 Using cached chart spec for exact match: {user_query[:50]}...")
                        # Always enhance cached chart spec before returning
                        enhanced_spec = self._enhance_chart_spec(cached_chart_spec, user_query)
                        return {
                            "chart_spec": enhanced_spec,
                            "from_cache": True,
                            "cache_hit": "exact_match",
                            "generation_method": "cache",
                            "chart_type": self._detect_chart_type(enhanced_spec)
                        }
        
        # Try LLM-based chart generation with improved prompting
        system_prompt = (
            "You are an expert data visualization specialist. Generate valid Vega-Lite JSON chart specifications "
            "from user prompts. Create realistic, relevant sample data that matches the user's request. "
            "Return ONLY the Vega-Lite JSON object, no extra text or explanations. "
            "Ensure the chart is well-styled, responsive, and follows best practices:\n"
            "- Include appropriate titles and axis labels\n"
            "- Use meaningful data that matches the request\n"
            "- Choose the right chart type for the data\n"
            "- Include proper styling and colors\n"
            "- Make sure the chart is readable and informative"
        )
        
        user_message = f"Create a Vega-Lite chart for: {prompt}\n\nGenerate realistic sample data that matches this request and return only the JSON specification."
        
        llm_response = chat_completion(
            messages=[{"role": "user", "content": user_message}],
            system_prompt=system_prompt,
            temperature=0.2,  # Lower temperature for more consistent results
            max_tokens=1500
        )
        
        # Try to parse the LLM response as JSON
        try:
            # Clean the response to extract JSON
            cleaned_response = self._extract_json_from_response(llm_response)
            chart_spec = json.loads(cleaned_response)
            
            # Validate and enhance the chart spec
            chart_spec = self._enhance_chart_spec(chart_spec, user_query or prompt)
            
            return {
                "chart_spec": chart_spec,
                "from_cache": False,
                "cache_hit": None,
                "generation_method": "llm",
                "chart_type": self._detect_chart_type(chart_spec)
            }
        except Exception as e:
            print(f"⚠️ LLM chart generation failed: {e}")
            # If LLM fails, generate dynamic mock data based on the query
            dynamic_spec = self._generate_dynamic_chart_spec(prompt, user_query)
            return {
                "chart_spec": dynamic_spec,
                "from_cache": False,
                "cache_hit": None,
                "generation_method": "dynamic_template",
                "llm_fallback": True,
                "llm_error": str(e),
                "chart_type": self._detect_chart_type(dynamic_spec)
            }
    
    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON from LLM response, handling common formatting issues."""
        # Remove markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end != -1:
                return response[start:end].strip()
        
        # Try to find JSON object
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end != -1:
            return response[start:end]
        
        return response.strip()
    
    def _enhance_chart_spec(self, chart_spec: Dict[str, Any], user_query: str) -> Dict[str, Any]:
        """Enhance a chart specification with modern, interactive, and responsive features."""
        # Ensure required fields
        if "$schema" not in chart_spec:
            chart_spec["$schema"] = "https://vega.github.io/schema/vega-lite/v5.json"
        # Responsive sizing
        chart_spec["autosize"] = {"type": "fit", "contains": "padding"}
        chart_spec["width"] = "container"
        chart_spec["height"] = "container"
        # Modern color scheme
        encoding = chart_spec.get("encoding", {})
        if "color" in encoding:
            if "scale" not in encoding["color"]:
                encoding["color"]["scale"] = {"scheme": "tableau10"}
            else:
                encoding["color"]["scale"]["scheme"] = "tableau10"
        else:
            encoding["color"] = {"field": "Region", "type": "nominal", "scale": {"scheme": "tableau10"}}
        # Bar corner radius and mark enhancements
        if "mark" in chart_spec:
            if isinstance(chart_spec["mark"], dict):
                chart_spec["mark"]["cornerRadiusEnd"] = 6
                chart_spec["mark"]["tooltip"] = True
            elif isinstance(chart_spec["mark"], str) and chart_spec["mark"] == "bar":
                chart_spec["mark"] = {"type": "bar", "cornerRadiusEnd": 6, "tooltip": True}
        # Add selection interactivity
        chart_spec["selection"] = {
            "highlight": {"type": "single", "on": "mouseover", "empty": "none"}
        }
        # Richer tooltips
        encoding["tooltip"] = [
            {"field": "Region", "type": "nominal", "title": "Region"},
            {"field": "Sales", "type": "quantitative", "title": "Sales (USD)"}
        ]
        # Clean axis titles (remove redundant 'title' at the same level as 'field')
        for axis in ["x", "y"]:
            if axis in encoding:
                if "title" in encoding[axis]:
                    # If axis.title exists, keep only axis.title
                    if "axis" in encoding[axis] and "title" in encoding[axis]["axis"]:
                        encoding[axis]["title"] = encoding[axis]["axis"]["title"]
                    # Remove redundant axis.title if both exist
                    if "axis" in encoding[axis] and "title" in encoding[axis]:
                        encoding[axis]["axis"]["title"] = encoding[axis]["title"]
                        del encoding[axis]["title"]
        chart_spec["encoding"] = encoding
        # Modern config
        chart_spec["config"] = {
            "bar": {"cornerRadiusEnd": 6},
            "axis": {"labelFontSize": 13, "titleFontSize": 16},
            "title": {"fontSize": 20, "fontWeight": "bold"}
        }
        return chart_spec
    
    def _detect_chart_type(self, chart_spec: Dict[str, Any]) -> str:
        """
        Detect the type of chart from the specification.
        
        Args:
            chart_spec (Dict[str, Any]): Chart specification
            
        Returns:
            str: Chart type (bar, line, scatter, etc.)
        """
        mark = chart_spec.get("mark", "")
        if isinstance(mark, dict):
            mark = mark.get("type", "")
        
        chart_types = {
            "bar": "bar",
            "line": "line", 
            "point": "scatter",
            "area": "area",
            "circle": "scatter",
            "square": "scatter",
            "tick": "tick",
            "rect": "heatmap",
            "rule": "rule",
            "text": "text"
        }
        
        return chart_types.get(mark.lower(), "unknown")
    
    def _generate_dynamic_chart_spec(self, prompt: str, user_query: str = "") -> Dict[str, Any]:
        """
        Generate a dynamic Vega-Lite chart specification based on the user's query.
        
        Args:
            prompt (str): Original prompt
            user_query (str): Original user query for context
            
        Returns:
            Dict[str, Any]: Dynamic Vega-Lite specification
        """
        # Analyze the query to determine appropriate data and chart type
        query_lower = (user_query or prompt).lower()
        
        # Determine chart type based on keywords
        if any(word in query_lower for word in ["bar", "column"]):
            chart_type = "bar"
        elif any(word in query_lower for word in ["line", "trend", "over time", "time series"]):
            chart_type = "line"
        elif any(word in query_lower for word in ["scatter", "point", "correlation"]):
            chart_type = "point"
        elif any(word in query_lower for word in ["pie", "donut"]):
            chart_type = "arc"
        elif any(word in query_lower for word in ["area", "stacked"]):
            chart_type = "area"
        else:
            chart_type = "bar"  # Default to bar chart
        
        # Generate appropriate data based on query content
        data, encoding, title = self._generate_dynamic_data(query_lower, chart_type)
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": f"Dynamic chart for: {user_query or prompt}",
            "data": {
                "values": data
            },
            "mark": chart_type,
            "encoding": encoding,
            "title": {
                "text": title,
                "fontSize": 16
            },
            "width": 600,
            "height": 400
        }
        
        return chart_spec
    
    def _generate_dynamic_data(self, query: str, chart_type: str) -> tuple:
        """
        Generate dynamic data based on the query content.
        
        Args:
            query (str): User query (lowercase)
            chart_type (str): Type of chart to generate
            
        Returns:
            tuple: (data, encoding, title)
        """
        # Common business metrics and dimensions
        metrics = ["revenue", "sales", "profit", "customers", "orders", "conversion_rate", "satisfaction_score", "churn_rate"]
        dimensions = ["region", "department", "product", "month", "quarter", "year", "category", "team"]
        
        # Determine what the user is asking about
        detected_metric = None
        detected_dimension = None
        
        for metric in metrics:
            if metric in query:
                detected_metric = metric
                break
        
        for dimension in dimensions:
            if dimension in query:
                detected_dimension = dimension
                break
        
        # Default values if not detected
        if not detected_metric:
            detected_metric = "revenue"
        if not detected_dimension:
            detected_dimension = "region"
        
        # Generate appropriate data based on the detected fields
        if detected_dimension == "month" or "time" in query or "trend" in query:
            return self._generate_time_series_data(detected_metric, chart_type)
        elif detected_dimension == "region":
            return self._generate_regional_data(detected_metric, chart_type)
        elif detected_dimension == "department":
            return self._generate_department_data(detected_metric, chart_type)
        elif detected_dimension == "product":
            return self._generate_product_data(detected_metric, chart_type)
        else:
            return self._generate_generic_data(detected_metric, detected_dimension, chart_type)
    
    def _generate_time_series_data(self, metric: str, chart_type: str) -> tuple:
        """Generate time series data."""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        if "churn" in metric:
            data = [{"month": month, "churn_rate": round(random.uniform(2, 8), 1)} for month in months[:6]]
            encoding = {
                "x": {"field": "month", "type": "ordinal", "title": "Month"},
                "y": {"field": "churn_rate", "type": "quantitative", "title": "Churn Rate (%)"}
            }
            title = "Customer Churn Rate Over Time"
        elif "satisfaction" in metric:
            data = [{"month": month, "satisfaction_score": round(random.uniform(3.5, 4.8), 1)} for month in months[:6]]
            encoding = {
                "x": {"field": "month", "type": "ordinal", "title": "Month"},
                "y": {"field": "satisfaction_score", "type": "quantitative", "title": "Satisfaction Score"}
            }
            title = "Customer Satisfaction Over Time"
        else:
            data = [{"month": month, "value": random.randint(50000, 200000)} for month in months[:6]]
            encoding = {
                "x": {"field": "month", "type": "ordinal", "title": "Month"},
                "y": {"field": "value", "type": "quantitative", "title": metric.title()}
            }
            title = f"{metric.title()} Over Time"
        
        return data, encoding, title
    
    def _generate_regional_data(self, metric: str, chart_type: str) -> tuple:
        """Generate regional data."""
        regions = ["North", "South", "East", "West", "Central"]
        
        if "churn" in metric:
            data = [{"region": region, "churn_rate": round(random.uniform(2, 12), 1)} for region in regions]
            encoding = {
                "x": {"field": "region", "type": "nominal", "title": "Region"},
                "y": {"field": "churn_rate", "type": "quantitative", "title": "Churn Rate (%)"}
            }
            title = "Customer Churn Rate by Region"
        elif "satisfaction" in metric:
            data = [{"region": region, "satisfaction_score": round(random.uniform(3.2, 4.9), 1)} for region in regions]
            encoding = {
                "x": {"field": "region", "type": "nominal", "title": "Region"},
                "y": {"field": "satisfaction_score", "type": "quantitative", "title": "Satisfaction Score"}
            }
            title = "Customer Satisfaction by Region"
        else:
            data = [{"region": region, "value": random.randint(80000, 250000)} for region in regions]
            encoding = {
                "x": {"field": "region", "type": "nominal", "title": "Region"},
                "y": {"field": "value", "type": "quantitative", "title": metric.title()}
            }
            title = f"{metric.title()} by Region"
        
        return data, encoding, title
    
    def _generate_department_data(self, metric: str, chart_type: str) -> tuple:
        """Generate department data."""
        departments = ["Sales", "Marketing", "Engineering", "Customer Support", "Finance", "HR"]
        
        if "churn" in metric:
            data = [{"department": dept, "churn_rate": round(random.uniform(1, 15), 1)} for dept in departments]
            encoding = {
                "x": {"field": "department", "type": "nominal", "title": "Department"},
                "y": {"field": "churn_rate", "type": "quantitative", "title": "Churn Rate (%)"}
            }
            title = "Employee Churn Rate by Department"
        elif "satisfaction" in metric:
            data = [{"department": dept, "satisfaction_score": round(random.uniform(3.0, 4.7), 1)} for dept in departments]
            encoding = {
                "x": {"field": "department", "type": "nominal", "title": "Department"},
                "y": {"field": "satisfaction_score", "type": "quantitative", "title": "Satisfaction Score"}
            }
            title = "Employee Satisfaction by Department"
        else:
            data = [{"department": dept, "value": random.randint(50000, 300000)} for dept in departments]
            encoding = {
                "x": {"field": "department", "type": "nominal", "title": "Department"},
                "y": {"field": "value", "type": "quantitative", "title": metric.title()}
            }
            title = f"{metric.title()} by Department"
        
        return data, encoding, title
    
    def _generate_product_data(self, metric: str, chart_type: str) -> tuple:
        """Generate product data."""
        products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        
        if "churn" in metric:
            data = [{"product": product, "churn_rate": round(random.uniform(3, 18), 1)} for product in products]
            encoding = {
                "x": {"field": "product", "type": "nominal", "title": "Product"},
                "y": {"field": "churn_rate", "type": "quantitative", "title": "Churn Rate (%)"}
            }
            title = "Customer Churn Rate by Product"
        elif "satisfaction" in metric:
            data = [{"product": product, "satisfaction_score": round(random.uniform(2.8, 4.6), 1)} for product in products]
            encoding = {
                "x": {"field": "product", "type": "nominal", "title": "Product"},
                "y": {"field": "satisfaction_score", "type": "quantitative", "title": "Satisfaction Score"}
            }
            title = "Customer Satisfaction by Product"
        else:
            data = [{"product": product, "value": random.randint(30000, 200000)} for product in products]
            encoding = {
                "x": {"field": "product", "type": "nominal", "title": "Product"},
                "y": {"field": "value", "type": "quantitative", "title": metric.title()}
            }
            title = f"{metric.title()} by Product"
        
        return data, encoding, title
    
    def _generate_generic_data(self, metric: str, dimension: str, chart_type: str) -> tuple:
        """Generate generic data for any metric/dimension combination."""
        categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
        
        if "churn" in metric:
            data = [{"category": cat, "churn_rate": round(random.uniform(2, 10), 1)} for cat in categories]
            encoding = {
                "x": {"field": "category", "type": "nominal", "title": dimension.title()},
                "y": {"field": "churn_rate", "type": "quantitative", "title": "Churn Rate (%)"}
            }
            title = f"Churn Rate by {dimension.title()}"
        elif "satisfaction" in metric:
            data = [{"category": cat, "satisfaction_score": round(random.uniform(3.5, 4.8), 1)} for cat in categories]
            encoding = {
                "x": {"field": "category", "type": "nominal", "title": dimension.title()},
                "y": {"field": "satisfaction_score", "type": "quantitative", "title": "Satisfaction Score"}
            }
            title = f"Satisfaction Score by {dimension.title()}"
        else:
            data = [{"category": cat, "value": random.randint(40000, 180000)} for cat in categories]
            encoding = {
                "x": {"field": "category", "type": "nominal", "title": dimension.title()},
                "y": {"field": "value", "type": "quantitative", "title": metric.title()}
            }
            title = f"{metric.title()} by {dimension.title()}"
        
        return data, encoding, title
    
    def _generate_mock_chart_spec(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a mock Vega-Lite chart specification for testing.
        
        Args:
            prompt (str): Original prompt (used for context)
            
        Returns:
            Dict[str, Any]: Mock Vega-Lite specification
        """
        # Mock data for testing
        mock_data = [
            {"region": "North", "revenue": 120000, "month": "Jan"},
            {"region": "South", "revenue": 95000, "month": "Jan"},
            {"region": "East", "revenue": 110000, "month": "Jan"},
            {"region": "West", "revenue": 85000, "month": "Jan"},
            {"region": "North", "revenue": 135000, "month": "Feb"},
            {"region": "South", "revenue": 105000, "month": "Feb"},
            {"region": "East", "revenue": 125000, "month": "Feb"},
            {"region": "West", "revenue": 90000, "month": "Feb"},
            {"region": "North", "revenue": 150000, "month": "Mar"},
            {"region": "South", "revenue": 115000, "month": "Mar"},
            {"region": "East", "revenue": 140000, "month": "Mar"},
            {"region": "West", "revenue": 100000, "month": "Mar"}
        ]
        
        chart_spec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
            "description": "Revenue by region over time",
            "data": {
                "values": mock_data
            },
            "mark": "line",
            "encoding": {
                "x": {
                    "field": "month",
                    "type": "ordinal",
                    "title": "Month"
                },
                "y": {
                    "field": "revenue",
                    "type": "quantitative",
                    "title": "Revenue ($)"
                },
                "color": {
                    "field": "region",
                    "type": "nominal",
                    "title": "Region"
                }
            },
            "title": {
                "text": "Revenue by Region Over Time",
                "fontSize": 16
            },
            "width": 600,
            "height": 400
        }
        
        return chart_spec
    
    def validate_chart_spec(self, chart_spec: Dict[str, Any]) -> bool:
        """
        Validate that the chart specification is properly formatted.
        
        Args:
            chart_spec (Dict[str, Any]): Chart specification to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["$schema", "data", "mark", "encoding"]
        
        for field in required_fields:
            if field not in chart_spec:
                return False
        
        return True
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for the agent.
        
        Args:
            state (Dict[str, Any]): Current state containing prompt
            
        Returns:
            Dict[str, Any]: Updated state with chart specification
        """
        prompt = state.get("prompt", "")
        user_query = state.get("user_query", "")
        
        if not prompt:
            raise ValueError("prompt is required in state")
        
        chart_result = self.build_chart(prompt, user_query)
        
        # Validate the chart specification
        is_valid = self.validate_chart_spec(chart_result["chart_spec"])
        
        return {
            **state,
            "chart_spec": chart_result["chart_spec"],
            "chart_spec_json": json.dumps(chart_result["chart_spec"]),
            "chart_valid": is_valid,
            "chart_from_cache": chart_result["from_cache"],
            "chart_cache_hit": chart_result["cache_hit"],
            "chart_generation_method": chart_result["generation_method"],
            "chart_type": chart_result["chart_type"],
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                "chart_builder": {
                    "chart_spec": chart_result["chart_spec"],
                    "chart_type": chart_result["chart_type"],
                    "from_cache": chart_result["from_cache"],
                    "cache_hit": chart_result["cache_hit"],
                    "generation_method": chart_result["generation_method"],
                    "is_valid": is_valid,
                    "status": "completed",
                    "llm_fallback": chart_result.get("llm_fallback", False),
                    "llm_error": chart_result.get("llm_error", None)
                }
            }
        }


# Example usage
if __name__ == "__main__":
    agent = ChartBuilderAgent()
    test_state = {
        "prompt": "Create a chart showing revenue by region over time"
    }
    result = agent.run(test_state)
    print(json.dumps(result, indent=2)) 