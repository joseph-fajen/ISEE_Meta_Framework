# ISEE Meta Framework - Web Demo

This is a minimalist web UI demo for showcasing the ISEE Meta Framework's configuration capabilities to potential investors.

## 🚀 Quick Start

### Option 1: Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Keys (Optional for simulation)**
   ```bash
   export OPENROUTER_API_KEY="your_key_here"
   export ANTHROPIC_API_KEY="your_key_here"  
   export OPENAI_API_KEY="your_key_here"
   export GOOGLE_API_KEY="your_key_here"
   ```

3. **Run the Demo**
   ```bash
   python app.py
   ```

4. **Open Browser**
   Navigate to `http://localhost:5001`

### Option 2: Docker

1. **Build and Run**
   ```bash
   docker-compose up --build
   ```

2. **Open Browser**
   Navigate to `http://localhost:5001`

## 🎯 Demo Features

### Configuration Interface
- **Innovation Query**: Large text input for problem statements
- **Cognitive Frameworks**: 10 selectable thinking approaches with icons (🔍💡⚖️🔗🔧🧱🌐🔄📚🚀)
- **AI Model Collections**: 8 curated OpenRouter collections with cost indicators
- **Knowledge Domains**: 8 categories with 58+ predefined domains
- **Execution Settings**: Variations, combinations, sampling method, output format

### Real-Time Preview Panel
- **Command Preview**: Generated terminal command display
- **Resource Estimation**: Cost, time, LLM calls, diversity score
- **Resource Guardrails**: Hardware-aware warnings and limits
- **Execution Progress**: Live progress tracking with status updates

### Investor Value Proposition
- **42.9x Model Diversity Expansion**: Clearly demonstrated through combinatorial selection
- **Resource Management**: Smart guardrails prevent runaway costs
- **Professional Interface**: Clean, modern UI suitable for executive demos
- **Transparent Execution**: Full visibility into command generation and execution

## 🎬 Demo Script for Investors

### 1. Innovation Challenge (30 seconds)
- Show the pre-filled sustainable transportation query
- Explain how ISEE transforms single prompts into systematic exploration

### 2. Cognitive Diversity (45 seconds)
- Select multiple cognitive frameworks (Analytical 🔍, Creative 💡, Systems 🌐)
- Show how each framework approaches problems differently
- Highlight the combinatorial multiplication effect

### 3. AI Model Portfolio (30 seconds)
- Select "Top Performers" collection (🏆)
- Show cost profiles: budget, balanced, premium
- Demonstrate access to 300+ models via OpenRouter

### 4. Domain Expertise (30 seconds)
- Select relevant domains (AI/ML, Strategy, Environmental Science)
- Show how domain selection informs the analysis
- Highlight cross-domain innovation potential

### 5. Resource Control (45 seconds)
- Adjust combinations to show cost estimation
- Trigger resource warnings to show guardrails
- Demonstrate the 42.9x diversity calculation

### 6. Execution Preview (30 seconds)
- Show generated command and cost breakdown
- Execute simulation to show progress tracking
- Download results to show deliverable output

**Total Demo Time: ~4 minutes**

## 🔧 Technical Architecture

### Backend Integration
- **Flask Web Server**: Lightweight Python web framework
- **Existing ISEE Logic**: Leverages all existing validation, cost estimation, and execution logic
- **Real-Time Updates**: AJAX-based parameter updates and cost estimation
- **Background Execution**: Threaded execution with progress polling

### Frontend Components
- **Single Page Application**: No page reloads, smooth UX
- **Responsive Design**: Works on laptops and large displays
- **Interactive Configuration**: Visual feedback for all selections
- **Professional Styling**: Modern gradient design suitable for investor presentations

### Resource Protection
- **Hardware Detection**: Laptop vs workstation limits
- **Cost Estimation**: Real API cost calculation
- **Progress Tracking**: Live execution monitoring
- **Error Recovery**: Graceful handling of execution failures

## 📊 Demo Metrics

### Performance Indicators
- **Setup Time**: < 2 minutes (local), < 5 minutes (Docker)
- **Demo Duration**: 4-6 minutes for full walkthrough
- **Response Time**: < 500ms for parameter updates
- **Resource Overhead**: Minimal (leverages existing ISEE backend)

### Investor Value Metrics
- **Model Diversity**: 42.9x expansion clearly demonstrated
- **Cost Control**: Hardware-appropriate guardrails active
- **Professional UX**: Enterprise-ready interface design
- **Technical Depth**: Full access to underlying ISEE capabilities

## 🚦 API Endpoints

### Configuration Endpoints
- `GET /api/frameworks` - Cognitive frameworks with icons
- `GET /api/collections` - OpenRouter model collections  
- `GET /api/domains` - Knowledge domain categories

### Execution Endpoints
- `POST /api/estimate` - Cost and resource estimation
- `POST /api/preview` - Command generation preview
- `POST /api/execute` - ISEE framework execution
- `GET /api/status/<id>` - Execution progress polling
- `GET /api/download/<id>` - Results file download

## 🔒 Security Considerations

### API Key Management
- Environment variable storage
- No client-side exposure
- Optional simulation mode (no keys required)

### Resource Protection
- Execution limits based on hardware detection
- Cost guardrails prevent runaway spending
- Progress monitoring with timeout protection

### Data Privacy
- No persistent storage of queries
- Temporary execution results with cleanup
- Local execution (no data sent to external services except AI APIs)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the correct directory
   cd /path/to/ISEE_Meta_Framework
   python app.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Change port in app.py or kill existing process
   lsof -ti:5000 | xargs kill
   ```

4. **API Key Issues**
   - Demo works in simulation mode without API keys
   - Add `--simulate` flag for dry runs
   - Check environment variable names

### Performance Tips
- Use simulation mode for faster demos
- Pre-select common configurations
- Keep execution combinations low for demos (12-24)

## 📝 Customization

### Branding
- Edit `templates/demo.html` for styling changes
- Modify header section for company branding
- Update color scheme in CSS section

### Configuration
- Adjust default selections in JavaScript initialization
- Modify domain categories in `app.py`
- Customize model collections via existing ISEE configuration

### Demo Content
- Update default query for your use case
- Pre-select relevant frameworks and domains
- Adjust execution settings for demo timing

## 🎯 Next Steps

After successful investor demo:

1. **Production Deployment**: Move to production-grade hosting
2. **Authentication**: Add user management and access control
3. **Analytics**: Track usage patterns and popular configurations
4. **API Integration**: Connect with customer systems and workflows
5. **Scaling**: Implement queue-based execution for high-volume usage

## 📞 Support

For demo setup assistance or customization requests, refer to the main ISEE documentation or contact the development team.

---

**ISEE Meta Framework**: Systematic AI-powered innovation through combinatorial exploration.