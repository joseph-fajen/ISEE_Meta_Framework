#!/usr/bin/env python3
"""
Launch script for the Cognitive Diversity Explorer
Creates a simple HTTP server to serve the web interface with real data.
"""

import json
import os
import http.server
import socketserver
import webbrowser
from pathlib import Path
import urllib.parse

class CognitiveDiversityHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, index_file, *args, **kwargs):
        self.index_file = index_file
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/api/cognitive_diversity_data':
            # Serve the cognitive diversity index as JSON API
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                self.wfile.write(json.dumps(data).encode('utf-8'))
            except Exception as e:
                error_response = {"error": str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        elif self.path.startswith('/api/raw-response?'):
            # Serve raw response files
            self.handle_raw_response_request()
        else:
            # Serve static files normally
            super().do_GET()
    
    def handle_raw_response_request(self):
        """Handle requests for raw response files."""
        try:
            # Parse the file parameter from query string
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            file_path = query_params.get('file', [None])[0]
            
            if not file_path:
                self.send_error(400, "Missing file parameter")
                return
            
            # Security: ensure the file path is within the expected directory structure
            # and doesn't contain path traversal attempts
            if '..' in file_path or file_path.startswith('/'):
                self.send_error(403, "Invalid file path")
                return
            
            # Construct full path to the raw response file
            run_directory = Path(self.index_file).parent
            full_file_path = run_directory / file_path
            
            if not full_file_path.exists():
                self.send_error(404, f"File not found: {file_path}")
                return
            
            # Read and serve the file content
            with open(full_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error reading file: {str(e)}")

def create_enhanced_web_interface(index_file: str, output_file: str):
    """Create an enhanced web interface that loads real data."""
    
    # Read the base template
    template_file = Path(__file__).parent / "cognitive_diversity_web.html"
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Replace the sample data loading with real API call
    js_replacement = """
        // Load real cognitive diversity data
        async function loadCognitiveDiversityData() {
            try {
                const response = await fetch('/api/cognitive_diversity_data');
                const data = await response.json();
                
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Extract run ID from the data
                if (data.run_directory) {
                    const runPath = data.run_directory;
                    currentRunId = runPath.split('/').pop(); // Extract run_YYYYMMDD_HHMMSS
                    console.log(`Set current run ID: ${currentRunId}`);
                } else {
                    // Fallback: use timestamp
                    currentRunId = `run_${new Date().toISOString().replace(/[-:]/g, '').split('.')[0].replace('T', '_')}`;
                    console.warn(`No run_directory found, using fallback: ${currentRunId}`);
                }
                
                allResponses = data.responses || [];
                filteredResponses = [...allResponses];
                
                // Now that we have the run ID, load run-specific annotations
                loadUserAnnotations();
                
                // Update stats
                const summary = data.summary || {};
                document.getElementById('totalResponses').textContent = summary.total_responses || allResponses.length;
                document.getElementById('avgScore').textContent = (summary.score_statistics?.mean || 0).toFixed(3);
                document.getElementById('frameworkCount').textContent = Object.keys(summary.framework_distribution || {}).length;
                document.getElementById('modelCount').textContent = Object.keys(summary.model_distribution || {}).length;
                
            } catch (error) {
                console.error('Error loading cognitive diversity data:', error);
                throw error;
            }
        }

        // Remove the sample data generation function
        function generateSampleData() {
            return []; // Real data loaded from API
        }
    """
    
    # Replace the sample data loading section
    content = content.replace(
        "// Simulate loading cognitive diversity data",
        "// Load real cognitive diversity data"
    )
    
    content = content.replace(
        "async function loadCognitiveDiversityData() {\n            // This would normally load from the JSON file\n            // For demonstration, we'll create sample data\n            allResponses = generateSampleData();\n            filteredResponses = [...allResponses];\n        }",
        js_replacement
    )
    
    # Write the enhanced interface
    with open(output_file, 'w') as f:
        f.write(content)

def launch_explorer(run_directory: str, port: int = 8080):
    """Launch the cognitive diversity explorer with a local server."""
    
    run_path = Path(run_directory)
    index_file = run_path / "cognitive_diversity_index.json"
    
    if not index_file.exists():
        print(f"❌ Cognitive diversity index not found: {index_file}")
        print("Please run the extractor first:")
        print(f"   python cognitive_diversity_extractor.py {run_directory}")
        return
    
    # Create enhanced web interface
    web_interface = run_path / "cognitive_diversity_explorer.html"
    create_enhanced_web_interface(str(index_file), str(web_interface))
    
    # Change to the run directory to serve files
    original_dir = os.getcwd()
    os.chdir(run_path)
    
    try:
        # Create custom handler with the index file
        def handler(*args, **kwargs):
            return CognitiveDiversityHandler(str(index_file), *args, **kwargs)
        
        # Start the server
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🧠 Cognitive Diversity Explorer")
            print(f"=" * 40)
            print(f"📊 Data source: {index_file}")
            print(f"🌐 Server running at: http://localhost:{port}")
            print(f"📱 Interface: http://localhost:{port}/cognitive_diversity_explorer.html")
            print(f"🔍 Ready to explore {len(json.load(open(str(index_file)))['responses'])} responses!")
            print(f"=" * 40)
            print(f"Press Ctrl+C to stop the server")
            
            # Open browser automatically
            webbrowser.open(f"http://localhost:{port}/cognitive_diversity_explorer.html")
            
            # Serve forever
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Happy exploring!")
    finally:
        os.chdir(original_dir)

def main():
    """Main execution function."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python launch_cognitive_explorer.py <run_directory> [port]")
        print("Example: python launch_cognitive_explorer.py data/output/run_20250812_133617 8080")
        sys.exit(1)
    
    run_directory = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    launch_explorer(run_directory, port)

if __name__ == "__main__":
    main()