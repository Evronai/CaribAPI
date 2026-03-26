#!/usr/bin/env python3
"""
Simple CaribAPI Data Dashboard (no external dependencies)
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class SimpleDataDashboard:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.dashboard_dir = self.project_root / "dashboard"
        self.dashboard_dir.mkdir(exist_ok=True)
    
    def load_latest_data(self) -> List[Dict]:
        """Load the latest business data"""
        # Look for latest JSON file
        json_files = list(self.project_root.glob("trinidad_businesses_*.json"))
        if not json_files:
            json_files = list(self.data_dir.glob("*.json"))
        
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
    
    def analyze_data(self, data: List[Dict]) -> Dict[str, Any]:
        """Analyze data quality"""
        if not data:
            return {}
        
        total = len(data)
        
        # Basic metrics
        active = sum(1 for r in data if r.get('status') == 'Active')
        verified = sum(1 for r in data if r.get('is_verified'))
        
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
        
        # Completeness
        completeness = {}
        fields_to_check = ['name', 'registration_number', 'city', 'industry', 'phone', 'email']
        for field in fields_to_check:
            complete = sum(1 for r in data if field in r and r[field])
            completeness[field] = {
                'count': complete,
                'percentage': (complete / total * 100) if total > 0 else 0
            }
        
        # Calculate overall score
        overall_score = 0
        if total > 0:
            # Simple scoring: 40% completeness, 30% accuracy, 30% distribution
            completeness_score = sum(c['percentage'] for c in completeness.values()) / len(completeness)
            accuracy_score = ((active / total * 50) + (verified / total * 50))
            
            # Distribution score (diversity)
            industry_diversity = min(100, len(industries) * 10)  # Up to 10 industries = 100%
            city_diversity = min(100, len(cities) * 20)  # Up to 5 cities = 100%
            distribution_score = (industry_diversity + city_diversity) / 2
            
            overall_score = (completeness_score * 0.4) + (accuracy_score * 0.3) + (distribution_score * 0.3)
        
        # Health assessment
        if overall_score >= 90:
            health = "✅ Excellent"
        elif overall_score >= 75:
            health = "🟢 Good"
        elif overall_score >= 60:
            health = "🟡 Fair"
        elif overall_score >= 40:
            health = "🟠 Needs Improvement"
        else:
            health = "🔴 Poor"
        
        return {
            'total_records': total,
            'active_count': active,
            'active_percentage': (active / total * 100) if total > 0 else 0,
            'verified_count': verified,
            'verified_percentage': (verified / total * 100) if total > 0 else 0,
            'industries': dict(sorted(industries.items(), key=lambda x: x[1], reverse=True)[:10]),
            'cities': dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]),
            'completeness': completeness,
            'overall_score': overall_score,
            'health': health,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_html_dashboard(self, analysis: Dict):
        """Generate HTML dashboard"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CaribAPI Data Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }}
        .logo {{ font-size: 2.5rem; font-weight: bold; margin-bottom: 10px; }}
        .timestamp {{ opacity: 0.8; font-size: 0.9rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .card h3 {{ color: #2d3748; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0; }}
        .metric {{ display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-value {{ font-weight: bold; font-size: 1.2rem; }}
        .health {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; }}
        .health-excellent {{ background: #48bb78; color: white; }}
        .health-good {{ background: #38a169; color: white; }}
        .health-fair {{ background: #ecc94b; color: #744210; }}
        .health-poor {{ background: #f56565; color: white; }}
        footer {{ text-align: center; margin-top: 40px; padding: 20px; color: #718096; }}
        @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
        
        /* Progress bars for completeness */
        .progress-container {{ width: 100%; background: #e2e8f0; border-radius: 10px; margin: 5px 0; }}
        .progress-bar {{ height: 10px; border-radius: 10px; background: #48bb78; }}
        
        /* Simple charts */
        .chart {{ display: flex; align-items: flex-end; height: 200px; gap: 10px; margin-top: 20px; }}
        .chart-bar {{ flex: 1; background: #667eea; border-radius: 5px 5px 0 0; position: relative; }}
        .chart-label {{ position: absolute; bottom: -25px; left: 0; right: 0; text-align: center; font-size: 0.8rem; color: #718096; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">CaribAPI Data Dashboard</div>
            <div class="timestamp">Last updated: {timestamp}</div>
        </header>
        
        <div class="grid">
            <!-- Overall Health -->
            <div class="card">
                <h3>📊 Overall Health</h3>
                <div class="metric">
                    <span>Status:</span>
                    <span class="health health-{analysis['health'].lower().replace(' ', '-').replace('✅', 'excellent').replace('🟢', 'good').replace('🟡', 'fair').replace('🔴', 'poor')}">
                        {analysis['health']}
                    </span>
                </div>
                <div class="metric">
                    <span>Score:</span>
                    <span class="metric-value">{analysis['overall_score']:.1f}/100</span>
                </div>
                <div class="metric">
                    <span>Total Records:</span>
                    <span class="metric-value">{analysis['total_records']:,}</span>
                </div>
            </div>
            
            <!-- Accuracy -->
            <div class="card">
                <h3>🎯 Accuracy</h3>
                <div class="metric">
                    <span>Active Businesses:</span>
                    <span class="metric-value">{analysis['active_count']:,} ({analysis['active_percentage']:.1f}%)</span>
                </div>
                <div class="metric">
                    <span>Verified Records:</span>
                    <span class="metric-value">{analysis['verified_count']:,} ({analysis['verified_percentage']:.1f}%)</span>
                </div>
            </div>
            
            <!-- Completeness -->
            <div class="card">
                <h3>📝 Completeness</h3>
"""
        
        # Add completeness bars
        for field, stats in analysis['completeness'].items():
            percentage = stats['percentage']
            html += f"""
                <div class="metric">
                    <span>{field.replace('_', ' ').title()}:</span>
                    <span>{percentage:.1f}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {percentage}%"></div>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <!-- Industry Distribution -->
        <div class="grid">
            <div class="card">
                <h3>🏆 Top Industries</h3>
                <div class="chart">
"""
        
        # Add industry chart bars
        industries = analysis['industries']
        if industries:
            max_count = max(industries.values())
            for industry, count in list(industries.items())[:8]:  # Top 8
                height = (count / max_count * 100) if max_count > 0 else 0
                html += f"""
                    <div class="chart-bar" style="height: {height}%">
                        <div class="chart-label">{industry[:10]}</div>
                    </div>
"""
        
        html += """
                </div>
                <div style="margin-top: 40px;">
"""
        
        # Industry list
        for i, (industry, count) in enumerate(list(industries.items())[:5], 1):
            percentage = (count / analysis['total_records'] * 100) if analysis['total_records'] > 0 else 0
            html += f"""
                    <div class="metric">
                        <span>{i}. {industry}</span>
                        <span>{count} ({percentage:.1f}%)</span>
                    </div>
"""
        
        html += """
                </div>
            </div>
            
            <!-- City Distribution -->
            <div class="card">
                <h3>📍 Top Cities</h3>
                <div class="chart">
"""
        
        # Add city chart bars
        cities = analysis['cities']
        if cities:
            max_count = max(cities.values())
            for city, count in list(cities.items())[:8]:  # Top 8
                height = (count / max_count * 100) if max_count > 0 else 0
                html += f"""
                    <div class="chart-bar" style="height: {height}%; background: #764ba2;">
                        <div class="chart-label">{city[:10]}</div>
                    </div>
"""
        
        html += """
                </div>
                <div style="margin-top: 40px;">
"""
        
        # City list
        for i, (city, count) in enumerate(list(cities.items())[:5], 1):
            percentage = (count / analysis['total_records'] * 100) if analysis['total_records'] > 0 else 0
            html += f"""
                    <div class="metric">
                        <span>{i}. {city}</span>
                        <span>{count} ({percentage:.1f}%)</span>
                    </div>
"""
        
        html += """
                </div>
            </div>
        </div>
        
        <!-- Data Summary -->
        <div class="card" style="margin-top: 30px;">
            <h3>📋 Data Summary</h3>
            <div class="grid" style="grid-template-columns: repeat(2, 1fr);">
                <div>
                    <h4>📈 Key Metrics</h4>
                    <div class="metric">
                        <span>Data Collection Date:</span>
                        <span>{timestamp}</span>
                    </div>
                    <div class="metric">
                        <span>Unique Industries:</span>
                        <span>{len(analysis['industries'])}</span>
                    </div>
                    <div class="metric">
                        <span>Unique Cities:</span>
                        <span>{len(analysis['cities'])}</span>
                    </div>
                </div>
                <div>
                    <h4>🚀 Next Steps</h4>
                    <div class="metric">
                        <span>Improve Completeness:</span>
                        <span>Add missing phone/email</span>
                    </div>
                    <div class="metric">
                        <span>Expand Coverage:</span>
                        <span>Add more cities</span>
                    </div>
                    <div class="metric">
                        <span>Increase Verification:</span>
                        <span>Verify more records</span>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>CaribAPI Data Dashboard • Generated on """ + timestamp + """</p>
            <p>This dashboard updates with each data collection run.</p>
            <p>Next scheduled update: Daily at 2:00 AM</p>
        </footer>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(() => location.reload(), 300000);
        
        // Update timestamp
        function updateTime() {
            const now = new Date();
            document.querySelector('.timestamp').textContent = 
                'Last updated: ' + now.toLocaleString();
        }
        setInterval(updateTime, 60000);
    </script>
</body>
</html>"""
        
        # Save HTML file
        html_file = self.dashboard_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML dashboard saved to: {html_file}")
        
        # Also save JSON data
        json_file = self.dashboard_dir / "data_analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✅ Data analysis saved to: {json_file}")
    
    def run(self):
        """Run the dashboard"""
        print("=" * 60)
        print("CaribAPI Simple Data Dashboard")
        print("=" * 60)
        
        # Load data
        data = self.load_latest_data()
        if not data:
            print("❌ No data available")
            return
        
        # Analyze
        analysis = self.analyze_data(data)
        
        # Print summary
        print(f"\n📋 Summary:")
        print(f"  Total Records: {analysis['total_records']:,}")
        print(f"  Health: {analysis['health']}")
        print(f"  Score: {analysis['overall_score']:.1f}/100")
        print(f"  Active: {analysis['active_count']:,} ({analysis['active_percentage']:.1f}%)")
        print(f"  Verified: {analysis['verified_count']:,} ({analysis['verified_percentage']:.1f}%)")
        
        print(f"\n🏆 Top 3 Industries:")
        for i, (industry, count) in enumerate(list(analysis['industries'].items())[:3], 1):
            percentage = (count / analysis['total_records'] * 100) if analysis['total_records'] > 0 else 0
            print(f"  {i}. {industry}: {count} ({percentage:.1f}%)")
        
        print(f"\n📍 Top 3 Cities:")
        for i, (city, count) in enumerate(list(analysis['cities'].items())[:3], 1):
            percentage = (count / analysis['total_records'] * 100) if analysis['total_records'] > 0 else 0
            print(f"  {i}. {city}: {count} ({percentage:.1f}%)")
        
        # Generate dashboard
        self.generate_html_dashboard(analysis)
        
        print(f"\n✅ Dashboard generated!")
        print(f"📁 Open: {self.dashboard_dir}/index.html")
        print(f"\n🎯 Next: Open the dashboard in your browser to see visualizations")

def main():
    dashboard = SimpleDataDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()