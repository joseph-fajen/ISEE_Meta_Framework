/* ISEE Fusion Prompting - Educational Visualization JavaScript */
/* Interactive demonstration of ISEE's combinatorial approach */

class ISEEFusionPrompting {
    constructor(containerId = 'fusion-rings-container') {
        this.containerId = containerId;
        this.rotations = {1: 0, 2: 0, 3: 0, 4: 0};
        this.autoRotateInterval = null;
        this.isInitialized = false;
        
        // Educational data representing ISEE's approach
        this.ringData = {
            1: {
                label: 'QV',
                name: 'Query Variations',
                items: [
                    'Original Query',
                    'Constraint-Based',
                    'Perspective-Shift', 
                    'Context-Enhanced',
                    'Rephrased Query',
                    'User-Focused'
                ],
                radius: 70,
                shadingPattern: 2,
                color: '#3498db',
                description: 'Different ways to phrase and approach your research question'
            },
            2: {
                label: 'CF',
                name: 'Cognitive Frameworks',
                items: [
                    'Analytical',
                    'Creative',
                    'Critical',
                    'Integrative', 
                    'Pragmatic',
                    'Systems Thinking'
                ],
                radius: 130,
                shadingPattern: 3,
                color: '#2ecc71',
                description: 'Different thinking approaches to analyze your question'
            },
            3: {
                label: 'KD',
                name: 'Knowledge Domains',
                items: [
                    'Technical Documentation',
                    'Knowledge Management',
                    'Content Strategy',
                    'Developer Experience',
                    'AI-Assisted Writing',
                    'Education Technology'
                ],
                radius: 190,
                shadingPattern: 4,
                color: '#9b59b6',
                description: 'Different knowledge areas to inform your analysis'
            },
            4: {
                label: 'LLM',
                name: 'AI Models',
                items: [
                    'Claude 3.5 Sonnet',
                    'GPT-4 Turbo',
                    'Gemini Pro',
                    'Llama 3.1',
                    'Mistral Large',
                    'Command R+'
                ],
                radius: 250,
                shadingPattern: 5,
                color: '#e67e22',
                description: 'Different AI models with unique capabilities and perspectives'
            }
        };
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.warn(`ISEE Fusion Prompting: Container ${this.containerId} not found`);
            return;
        }
        
        this.createRings();
        this.setupEventListeners();
        this.updateCurrentCombination();
        this.updateSamplingStats();
        
        this.isInitialized = true;
        console.log('ISEE Fusion Prompting initialized successfully');
    }
    
    createRings() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        // Create alignment indicators
        const indicators = [
            {top: 40, left: 298},
            {top: 100, left: 298},
            {top: 160, left: 298},
            {top: 220, left: 298}
        ];
        
        indicators.forEach(pos => {
            const indicator = document.createElement('div');
            indicator.className = 'fusion-alignment-indicator';
            indicator.style.top = `${pos.top}px`;
            indicator.style.left = `${pos.left}px`;
            container.appendChild(indicator);
        });
        
        // Create rings
        Object.keys(this.ringData).forEach(ringNum => {
            const ring = document.createElement('div');
            ring.className = `fusion-ring fusion-ring-${ringNum}`;
            ring.id = `fusion-ring-${ringNum}`;
            ring.title = this.ringData[ringNum].description;
            
            const data = this.ringData[ringNum];
            const segmentAngle = 360 / data.items.length;
            
            data.items.forEach((item, index) => {
                const segment = document.createElement('div');
                segment.className = 'fusion-ring-segment';
                
                const angle = index * segmentAngle;
                const radian = (angle - 90) * Math.PI / 180;
                const x = data.radius * Math.cos(radian);
                const y = data.radius * Math.sin(radian);
                
                segment.style.left = '50%';
                segment.style.top = '50%';
                segment.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
                
                const text = document.createElement('span');
                text.className = 'fusion-ring-text';
                text.textContent = `${data.label}${index + 1}`;
                text.title = `${data.name}: ${item}`;
                
                // Apply educational shading pattern
                if ((index + 1) % data.shadingPattern === 0) {
                    segment.classList.add('fusion-shaded');
                }
                
                segment.appendChild(text);
                ring.appendChild(segment);
            });
            
            container.appendChild(ring);
        });
        
        // Create center label
        const centerLabel = document.createElement('div');
        centerLabel.className = 'fusion-center-label';
        centerLabel.textContent = 'Query';
        centerLabel.title = 'Your research question sits at the center, surrounded by the four dimensions of ISEE analysis';
        container.appendChild(centerLabel);
    }
    
    setupEventListeners() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        
        // Add click handlers for individual ring rotation
        container.addEventListener('click', (e) => {
            // Get click coordinates relative to container
            const rect = container.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const clickX = e.clientX - rect.left;
            const clickY = e.clientY - rect.top;
            
            // Calculate distance from center
            const distanceFromCenter = Math.sqrt(
                Math.pow(clickX - centerX, 2) + Math.pow(clickY - centerY, 2)
            );
            
            // Define ring boundaries with tolerance zones for easy clicking
            const tolerance = 10; // pixels of tolerance on both sides of each ring
            let ringToRotate = null;
            
            // Ring 1 (Blue) - Query Variations: actual ring at ~70px radius
            const ring1Inner = 70 - 17.5 - tolerance;  // inner edge minus tolerance
            const ring1Outer = 70 + 17.5 + tolerance;  // outer edge plus tolerance
            
            // Ring 2 (Green) - Cognitive Frameworks: actual ring at ~130px radius  
            const ring2Inner = 130 - 17.5 - tolerance;
            const ring2Outer = 130 + 17.5 + tolerance;
            
            // Ring 3 (Purple) - Knowledge Domains: actual ring at ~190px radius
            const ring3Inner = 190 - 17.5 - tolerance;
            const ring3Outer = 190 + 17.5 + tolerance;
            
            // Ring 4 (Orange) - AI Models: actual ring at ~250px radius
            const ring4Inner = 250 - 17.5 - tolerance;
            const ring4Outer = 250 + 17.5 + tolerance;
            
            // Check each ring's click zone (with no overlap between rings)
            if (distanceFromCenter >= ring1Inner && distanceFromCenter <= ring1Outer) {
                ringToRotate = 1; // Blue ring
            } else if (distanceFromCenter >= ring2Inner && distanceFromCenter <= ring2Outer) {
                ringToRotate = 2; // Green ring
            } else if (distanceFromCenter >= ring3Inner && distanceFromCenter <= ring3Outer) {
                ringToRotate = 3; // Purple ring
            } else if (distanceFromCenter >= ring4Inner && distanceFromCenter <= ring4Outer) {
                ringToRotate = 4; // Orange ring
            }
            
            if (ringToRotate) {
                this.rotateRing(ringToRotate);
            }
        });
        
        // Setup control buttons
        this.setupControlButtons();
    }
    
    setupControlButtons() {
        const buttonMappings = [
            {id: 'fusion-rotate-variations', ring: 1},
            {id: 'fusion-rotate-frameworks', ring: 2},
            {id: 'fusion-rotate-domains', ring: 3},
            {id: 'fusion-rotate-models', ring: 4},
            {id: 'fusion-auto-rotate', action: 'auto'},
            {id: 'fusion-reset', action: 'reset'}
        ];
        
        buttonMappings.forEach(mapping => {
            const button = document.getElementById(mapping.id);
            if (button) {
                button.addEventListener('click', () => {
                    if (mapping.action === 'auto') {
                        this.autoRotate();
                    } else if (mapping.action === 'reset') {
                        this.resetRings();
                    } else {
                        this.rotateRing(mapping.ring);
                    }
                });
            }
        });
    }
    
    rotateRing(ringNum) {
        const ring = document.getElementById(`fusion-ring-${ringNum}`);
        if (!ring) return;
        
        const data = this.ringData[ringNum];
        const segmentAngle = 360 / data.items.length;
        this.rotations[ringNum] -= segmentAngle;
        
        ring.style.transform = `rotate(${this.rotations[ringNum]}deg)`;
        
        // Add pulse animation
        ring.classList.add('animate-pulse');
        setTimeout(() => {
            ring.classList.remove('animate-pulse');
        }, 1000);
        
        this.updateCurrentCombination();
        this.updateSamplingStats();
    }
    
    updateCurrentCombination() {
        // Update the current combination display
        const getItemIndex = (rotation, itemCount) => {
            const segmentAngle = 360 / itemCount;
            let index = Math.floor(((rotation % 360) + 360) % 360 / segmentAngle);
            return Math.max(0, Math.min(index, itemCount - 1));
        };
        
        const updates = {
            'fusion-current-qv': this.ringData[1].items[getItemIndex(this.rotations[1], this.ringData[1].items.length)],
            'fusion-current-cf': this.ringData[2].items[getItemIndex(this.rotations[2], this.ringData[2].items.length)],
            'fusion-current-kd': this.ringData[3].items[getItemIndex(this.rotations[3], this.ringData[3].items.length)],
            'fusion-current-llm': this.ringData[4].items[getItemIndex(this.rotations[4], this.ringData[4].items.length)]
        };
        
        Object.keys(updates).forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                element.textContent = updates[elementId];
            }
        });
    }
    
    updateSamplingStats() {
        // Educational statistics showing ISEE's sampling approach
        const totalCombinations = Math.pow(6, 4); // 1,296 combinations
        const sampledCount = Math.min(100, Math.floor(totalCombinations * 0.077)); // Realistic sampling
        const diversityScore = Math.floor(75 + Math.random() * 20); // 75-95% diversity
        
        const sampledElement = document.getElementById('fusion-sampled-count');
        const diversityElement = document.getElementById('fusion-diversity-score');
        
        if (sampledElement) {
            sampledElement.textContent = sampledCount;
        }
        
        if (diversityElement) {
            diversityElement.textContent = diversityScore + '%';
        }
    }
    
    autoRotate() {
        const button = document.getElementById('fusion-auto-rotate');
        
        if (this.autoRotateInterval) {
            clearInterval(this.autoRotateInterval);
            this.autoRotateInterval = null;
            if (button) {
                button.textContent = 'Auto Rotate';
                button.style.background = 'linear-gradient(135deg, var(--color-primary-start), var(--color-primary-end))';
            }
            return;
        }
        
        if (button) {
            button.textContent = 'Stop Auto';
            button.style.background = 'linear-gradient(135deg, var(--color-error), #c53030)';
        }
        
        this.autoRotateInterval = setInterval(() => {
            const ringToRotate = Math.floor(Math.random() * 4) + 1;
            this.rotateRing(ringToRotate);
        }, 1200); // Slightly slower for educational purposes
    }
    
    resetRings() {
        if (this.autoRotateInterval) {
            clearInterval(this.autoRotateInterval);
            this.autoRotateInterval = null;
            const button = document.getElementById('fusion-auto-rotate');
            if (button) {
                button.textContent = 'Auto Rotate';
                button.style.background = 'linear-gradient(135deg, var(--color-primary-start), var(--color-primary-end))';
            }
        }
        
        this.rotations = {1: 0, 2: 0, 3: 0, 4: 0};
        
        Object.keys(this.ringData).forEach(ringNum => {
            const ring = document.getElementById(`fusion-ring-${ringNum}`);
            if (ring) {
                ring.style.transform = 'rotate(0deg)';
            }
        });
        
        this.updateCurrentCombination();
        this.updateSamplingStats();
    }
    
    // Public methods for external integration
    getCurrentCombination() {
        const combination = {};
        Object.keys(this.ringData).forEach(ringNum => {
            const data = this.ringData[ringNum];
            const segmentAngle = 360 / data.items.length;
            let currentIndex = Math.floor(((this.rotations[ringNum] % 360) + 360) % 360 / segmentAngle);
            currentIndex = Math.max(0, Math.min(currentIndex, data.items.length - 1));
            combination[data.name] = data.items[currentIndex];
        });
        return combination;
    }
    
    getStats() {
        return {
            totalCombinations: Math.pow(6, 4),
            sampledCombinations: Math.min(100, Math.floor(Math.pow(6, 4) * 0.077)),
            diversityScore: Math.floor(75 + Math.random() * 20)
        };
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if the fusion prompting container exists
    if (document.getElementById('fusion-rings-container')) {
        window.iseeFusionPrompting = new ISEEFusionPrompting();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ISEEFusionPrompting;
}