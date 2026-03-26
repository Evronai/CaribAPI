#!/usr/bin/env python3
"""
CaribAPI Data Verification Dashboard
Provides insights into data quality, completeness, and updates
"""
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class DataDashboard:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Dashboard output directory
        self.dashboard_dir = self.project_root / "dashboard"
        self.dashboard_dir.mkdir(exist_ok=True)
    
    def load_latest_data(self) -> List[Dict]:
        """Load the latest business data"""
        # Look for latest JSON file
        json_files = list(self.data_dir.glob("*.json"))
        if not json_files:
            # Fall back to project root
            json_files = list(self.project_root.glob("trinidad_businesses_*.json"))
        
        if not json_files:
            print("❌ No data files found")
            return []
        
        # Get most recent file
        latest_file = max(json_files, key=os.path.getmtime)
        print(f"📁 Loading data from: {latest_file.name}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Loaded {len(data)} business records")
        return data
    
    def analyze_data_quality(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze data quality metrics"""
        print("\n🔍 Analyzing Data Quality...")
        
        if not data:
            return {}
        
        total = len(data)
        
        # Completeness analysis
        required_fields = [
            'name', 'registration_number', 'city', 'industry', 
            'status', 'phone', 'email', 'website'
        ]
        
        optional_fields = [
            'annual_revenue_range', 'employee_count_range',
            'directors', 'is_verified', 'verification_score'
        ]
        
        completeness = {}
        for field in required_fields + optional_fields:
            complete = sum(1 for record in data if field in record and record[field])
            completeness[field] = {
                'count': complete,
                'percentage': (complete / total * 100) if total > 0 else 0
            }
        
        # Accuracy indicators
        active_count = sum(1 for r in data if r.get('status') == 'Active')
        verified_count = sum(1 for r in data if r.get('is_verified'))
        
        # Data freshness
        today = datetime.now()
        freshness_counts = {'<7 days': 0, '7-30 days': 0, '30-90 days': 0, '>90 days': 0}
        
        for record in data:
            last_updated = record.get('last_updated')
            if last_updated:
                try:
                    if isinstance(last_updated, str):
                        update_date = datetime.strptime(last_updated, '%Y-%m-%d')
                    else:
                        update_date = last_updated
                    
                    days_old = (today - update_date).days
                    
                    if days_old < 7:
                        freshness_counts['<7 days'] += 1
                    elif days_old < 30:
                        freshness_counts['7-30 days'] += 1
                    elif days_old < 90:
                        freshness_counts['30-90 days'] += 1
                    else:
                        freshness_counts['>90 days'] += 1
                except:
                    pass
        
        # Industry distribution
        industries = {}
        for record in data:
            industry = record.get('industry', 'Unknown')
            industries[industry] = industries.get(industry, 0) + 1
        
        # City distribution
        cities = {}
        for record in data:
            city = record.get('city', 'Unknown')
            cities[city] = cities.get(city, 0) + 1
        
        # Business type distribution
        business_types = {}
        for record in data:
            biz_type = record.get('business_type', 'Unknown')
            business_types[biz_type] = business_types.get(biz_type, 0) + 1
        
        quality_report = {
            'total_records': total,
            'completeness': completeness,
            'accuracy': {
                'active_count': active_count,
                'active_percentage': (active_count / total * 100) if total > 0 else 0,
                'verified_count': verified_count,
                'verified_percentage': (verified_count / total * 100) if total > 0 else 0,
            },
            'freshness': freshness_counts,
            'distributions': {
                'industries': dict(sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]),
                'cities': dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]),
                'business_types': business_types,
            },
            'summary': {
                'overall_score': self._calculate_overall_score(completeness, active_count, verified_count, total),
                'data_health': self._assess_data_health(completeness, active_count, verified_count, total),
            }
        }
        
        return quality_report
    
    def _calculate_overall_score(self, completeness: Dict, active_count: int, verified_count: int, total: int) -> float:
        """Calculate overall data quality score (0-100)"""
        if total == 0:
            return 0
        
        # Weighted scoring
        weights = {
            'completeness': 0.4,
            'accuracy': 0.3,
            'freshness': 0.2,
            'distribution': 0.1,
        }
        
        # Completeness score (average of required fields)
        required_fields = ['name', 'registration_number', 'city', 'industry', 'status']
        completeness_score = sum(completeness.get(field, {}).get('percentage', 0) for field in required_fields) / len(required_fields)
        
        # Accuracy score
        accuracy_score = (active_count / total * 50) + (verified_count / total * 50)
        
        # Freshness score (assume most data is fresh for now)
        freshness_score = 80  # Placeholder
        
        # Distribution score (diversity of industries/cities)
        distribution_score = 70  # Placeholder
        
        overall = (
            completeness_score * weights['completeness'] +
            accuracy_score * weights['accuracy'] +
            freshness_score * weights['freshness'] +
            distribution_score * weights['distribution']
        )
        
        return min(100, overall)
    
    def _assess_data_health(self, completeness: Dict, active_count: int, verified_count: int, total: int) -> str:
        """Assess overall data health"""
        if total == 0:
            return "❌ No Data"
        
        overall_score = self._calculate_overall_score(completeness, active_count, verified_count, total)
        
        if overall_score >= 90:
            return "✅ Excellent"
        elif overall_score >= 75:
            return "🟢 Good"
        elif overall_score >= 60:
            return "🟡 Fair"
        elif overall_score >= 40:
            return "🟠 Needs Improvement"
        else:
            return "🔴 Poor"
    
    def generate_visualizations(self, data: List[Dict], quality_report: Dict):
        """Generate data visualizations"""
        print("\n📈 Generating Visualizations...")
        
        # Create visualizations directory
        viz_dir = self.dashboard_dir / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # 1. Industry Distribution Pie Chart
        industries = quality_report['distributions']['industries']
        if industries:
            plt.figure(figsize=(10, 6))
            plt.pie(industries.values(), labels=industries.keys(), autopct='%1.1f%%')
            plt.title('Business Distribution by Industry')
            plt.tight_layout()
            plt.savefig(viz_dir / 'industry_distribution.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  ✅ Industry distribution chart saved")
        
        # 2. City Distribution Bar Chart
        cities = quality_report['distributions']['cities']
        if cities:
            plt.figure(figsize=(12, 6))
            plt.bar(cities.keys(), cities.values())
            plt.title('Business Distribution by City')
            plt.xlabel('City')
            plt.ylabel('Number of Businesses')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(viz_dir / 'city_distribution.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  ✅ City distribution chart saved")
        
        # 3. Completeness Heatmap
        completeness = quality_report['completeness']
        if completeness:
            fields = list(completeness.keys())
            percentages = [completeness[field]['percentage'] for field in fields]
            
            plt.figure(figsize=(12, 6))
            colors = ['red' if p < 50 else 'orange' if p < 80 else 'green' for p in percentages]
            bars = plt.bar(fields, percentages, color=colors)
            plt.title('Data Completeness by Field')
            plt.xlabel('Field')
            plt.ylabel('Completion Percentage')
            plt.ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, percentage in zip(bars, percentages):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            plt.savefig(viz_dir / 'completeness_heatmap.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  ✅ Completeness heatmap saved")
        
        # 4. Data Freshness Chart
        freshness = quality_report['freshness']
        if freshness:
            plt.figure(figsize=(8, 6))
            plt.pie(freshness.values(), labels=freshness.keys(), autopct='%1.1f%%')
            plt.title('Data Freshness (Days Since Last Update)')
            plt.tight_layout()
            plt.savefig(viz_dir / 'data_freshness.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("  ✅ Data freshness chart saved")
        
        print(f"  📁 Visualizations saved to: {viz_dir}")
    
    def generate_html_dashboard(self, quality_report: Dict):
        """Generate HTML dashboard"""
        print("\n🌐 Generating HTML Dashboard...")
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CaribAPI Data Dashboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: #f5f5f5;
                    padding: 20px;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                
                .logo {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                
                .timestamp {{
                    opacity: 0.8;
                    font-size: 0.9rem;
                }}
                
                .dashboard-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                
                .card {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                
                .card h3 {{
                    color: #2d3748;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #e2e8f0;
                }}
                
                .metric {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                
                .metric:last-child {{
                    border-bottom: none;
                }}
                
                .metric-value {{
                    font-weight: bold;
                    font-size: 1.2rem;
                }}
                
                .health-indicator {{
                    display: inline-block;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 0.9rem;
                }}
                
                .health-excellent {{ background: #48bb78; color: white; }}
                .health-good {{ background: #38a169; color: white; }}
                .health-fair {{ background: #ecc94b; color: #744210; }}
                .health-needs-improvement {{ background: #ed8936; color: white; }}
                .health-poor {{ background: #f56565; color: white; }}
                
                .visualizations {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }}
                
                .viz-card {{
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                
                .viz-card img {{
                    width: 100%;
                    height: auto;
                    border-radius: 5px;
                }}
                
                footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #718096;
                    font-size: 0.9rem;
                }}
                
                @media (max-width: 768px) {{
                    .dashboard-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .visualizations {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <div class="logo">CaribAPI Data Dashboard</div>
                    <div class="timestamp">Last updated: {timestamp}</div>
                </header>
                
                <div class="dashboard-grid">
                    <!-- Overall Health Card -->
                    <div class="card">
                        <h3>📊 Overall Data Health</h3>
                        <div class="metric">
                            <span>Health Status:</span>
                            <span class="health-indicator health-{quality_report['summary']['data_health'].lower().replace(' ', '-').replace('❌', 'poor').replace('✅', 'excellent').replace('🟢', 'good').replace('🟡', 'fair').replace('🟠', 'needs-improvement').replace('🔴', 'poor')}">
                                {quality_report['summary']['data_health']}
                            </span>
                        </div>
                        <div class="metric">
                            <span>Quality Score:</span>
                            <span class="metric-value">{quality_report['summary']['overall_score']:.1f}/100</span>
                        </div>
                        <div class="metric">
                            <span>Total Records:</span>
                            <span class="metric-value">{quality_report['total_records']:,}</span>
                        </div>
                    </div>
                    
                    <!-- Accuracy Card -->
                    <div class="card">
                        <h3>🎯 Data Accuracy</h3>
                        <div class="metric">
                            <span>Active Businesses:</span>
                            <span class="metric-value">{quality_report['accuracy']['active_count']:,} ({quality_report['accuracy']['active_percentage']:.1f}%)</span>
                        </div>
                        <div class="metric">
                            <span>Verified Records:</span>
                            <span class="metric-value">{quality_report['accuracy']['verified_count']:,} ({quality_report['accuracy']['verified_percentage']:.1f}%)</span>
                        </div>
                    </div>
                    
                    <!-- Completeness Card -->
                    <div class="card">
                        <h3>📝 Data Completeness</h3>
        """
        
        # Add completeness metrics for key fields
        key_fields = ['name', 'registration_number', 'city', 'industry', 'phone', 'email']
        for field in key_fields:
            if field in quality_report['completeness']:
                perc = quality_report['completeness'][field]['percentage']
                html_content += f"""
                        <div class="metric">
                            <span>{field.replace('_', ' ').title()}:</span>
                            <span class="metric-value">{perc:.1f}%</span>
                        </div>
                """
        
        html_content += """
                    </div>
                    
                    <!-- Freshness Card -->
                    <div class="card">
                        <h3>🕒 Data Freshness</h3>
        """
        
        # Add freshness metrics
        for period, count in quality_report['freshness'].items():
            percentage = (count / quality_report['total_records'] * 100) if quality_report['total_records'] > 0 else 0
            html_content += f"""
                        <div class="metric">
                            <span>{period}:</span>
                            <span class="metric-value">{count} ({percentage:.1f}%)</span>
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
                
                <!-- Visualizations Section -->
                <h2 style="margin: 30px 0 20px 0; color: #2d3748;">📈 Data Visualizations</h2>
                <div class="visualizations">
                    <div class="viz-card">
                        <h3>Industry Distribution</h3>
                        <img src="visualizations/industry_distribution.png" alt="Industry Distribution">
                    </div>
                    
                    <div class="viz-card">
                        <h3>City Distribution</h3>
                        <img src="visualizations/city_distribution.png" alt="City Distribution">
                    </div>
                    
                    <div class="viz-card">
                        <h3>Data Completeness</h3>
                        <img src="visualizations/completeness_heatmap.png" alt="Completeness Heatmap">
                    </div>
                    
                    <div class="viz-card">
                        <h3>Data Freshness</h3>
                        <img src="visualizations/data_freshness.png" alt="Data Freshness">
                    </div>
                </div>
                
                <!-- Top Industries & Cities -->
                <div class="dashboard-grid" style="margin-top: 30px;">
                    <div class="card">
                        <h3>🏆 Top 5 Industries</h3>
        """
        
        # Add top industries
        for i, (industry, count) in enumerate(list(quality_report['distributions']['industries'].items())[:5], 1):
            percentage = (count / quality_report['total_records'] * 100) if quality_report['total_records'] > 0 else 0
            html_content += f"""
                        <div class="metric">
                            <span>{i}. {industry}</span>
                            <span class="metric-value">{count} ({percentage:.1f}%)</span>
                        </div>
            """
        
        html_content += """
                    </div>
                    
                    <div class="card">
                        <h3>📍 Top 5 Cities</h3>
        """
        
        # Add top cities
        for i, (city, count) in enumerate(list(quality_report['distributions']['cities'].items())[:5], 1):
            percentage = (count / quality_report['total_records'] * 100) if quality_report['total_records'] > 0 else 0
            html_content += f"""
                        <div class="metric">
                            <span>{i}. {city}</span>
                            <span class="metric-value">{count} ({percentage:.1f}%)</span>
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
                
                <footer>
                    <p>CaribAPI Data Dashboard • Generated on {}</p>
                    <p>This dashboard updates automatically with each data collection run.</p>
                    <p>Next scheduled update: Daily at 2:00 AM</p>
                </footer>
            </div>
            
            <script>
                // Auto-refresh dashboard every 5 minutes
                setTimeout(function() {{
                    location.reload();
                }}, 300000);
                
                // Update timestamp every minute
                function updateTimestamp() {{
                    const now = new Date();
                    const timestamp = now.toLocaleString();
                    document.querySelector('.timestamp').textContent = 'Last updated: ' + timestamp;
                }}
                
                setInterval(updateTimestamp, 60000);
            </script>
        </body>
        </html>
        """.format(timestamp)
        
        # Save HTML file
        html_file = self.dashboard_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ HTML dashboard saved to: {html_file}")
        
        # Also save JSON report
        json_file = self.dashboard_dir / "quality_report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(quality_report, f, indent=2, default=str)
        
        print(f"  ✅ Quality report saved to: {json_file}")
    
    def run_dashboard(self):
        """Run the complete dashboard generation"""
        print("=" * 60)
        print("CaribAPI Data Verification Dashboard")
        print("=" * 60)
        
        # Load data
        data = self.load_latest_data()
        if not data:
            print("❌ No data available for dashboard")
            return
        
        # Analyze data quality
        quality_report = self.analyze_data_quality(data)
        
        if not quality_report:
            print("❌ Could not generate quality report")
            return
        
        # Print summary to console
        print("\n" + "=" * 60)
        print("📋 Data Quality Summary")
        print("=" * 60)
        
        print(f"Total Records: {quality_report['total_records']:,}")
        print(f"Overall Health: {quality_report['summary']['data_health']}")
        print(f"Quality Score: {quality_report['summary']['overall_score']:.1f}/100")
        
        print(f"\n📊 Accuracy:")
        print(f"  Active Businesses: {quality_report['accuracy']['active_count']:,} ({quality_report['accuracy']['active_percentage']:.1f}%)")
        print(f"  Verified Records: {quality_report['accuracy']['verified_count']:,} ({quality_report['accuracy']['verified_percentage']:.1f}%)")
        
        print(f"\n📝 Completeness (Key Fields):")
        key_fields = ['name', 'registration_number', 'city', 'industry', 'phone']
        for field in key_fields:
            if field in quality_report['completeness']:
                perc = quality_report['completeness'][field]['percentage']
                print(f"  {field.replace('_', ' ').title()}: {perc:.1f}%")
        
        print(f"\n🕒 Data Freshness:")
        for period, count in quality_report['freshness'].items():
            percentage = (count / quality_report['total_records'] * 100) if quality_report['total_records'] > 0 else 0
            print(f"  {period}: {count} ({percentage:.1f}%)")
        
        print(f"\n🏆 Top 3 Industries:")
        for i, (industry, count) in enumerate(list(quality_report['distributions']['industries'].items())[:3], 1):
            percentage = (count / quality_report['total_records'] * 100) if quality_report['total_records'] > 0 else 0
            print(f"  {i}. {industry}: {count} ({percentage:.1f}%)")
        
        # Generate visualizations
        self.generate_visualizations(data, quality_report)
        
        # Generate HTML dashboard
        self.generate_html_dashboard(quality_report)
        
        print("\n" + "=" * 60)
        print("🎉 Dashboard Generation Complete!")
        print("=" * 60)
        print(f"📁 Dashboard files saved to: {self.dashboard_dir}")
        print(f"🌐 Open dashboard: {self.dashboard_dir}/index.html")
        print("\n📈 Next Steps:")
        print("1. Open the HTML dashboard in your browser")
        print("2. Check data quality metrics regularly")
        print("3. Use insights to improve data collection")
        print("4. Share dashboard with stakeholders")

def main():
    """Main function"""
    dashboard = DataDashboard()
    dashboard.run_dashboard()

if __name__ == "__main__":
    main()