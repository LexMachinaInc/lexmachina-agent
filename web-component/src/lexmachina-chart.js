/**
 * LexMachina Chart Web Component
 * A standalone, framework-agnostic web component for displaying box plots and timing line charts
 * using D3.js for legal data visualization.
 * 
 * @license Apache-2.0
 */

/**
 * Custom element for displaying box plots or timing line charts
 * Can be used with any framework (React, Angular, Vue, etc.) or vanilla JavaScript
 * 
 * Usage:
 *   <lexmachina-chart type="boxplot" data='[...]'></lexmachina-chart>
 *   <lexmachina-chart type="timeline" data='[...]'></lexmachina-chart>
 * 
 * Attributes:
 *   - type: "boxplot" or "timeline" (default: "boxplot")
 *   - data: JSON string or object with chart data
 *   - width: Chart width in pixels (default: 600)
 *   - height: Chart height in pixels (default: 400)
 *   - title: Chart title (optional)
 */
class LexMachinaChart extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this._data = null;
        this._type = 'boxplot';
        this._width = 600;
        this._height = 400;
        this._title = '';
    }

    static get observedAttributes() {
        return ['type', 'data', 'width', 'height', 'title'];
    }

    connectedCallback() {
        this.render();
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue === newValue) return;

        switch (name) {
            case 'type':
                this._type = newValue || 'boxplot';
                break;
            case 'data':
                try {
                    this._data = typeof newValue === 'string' ? JSON.parse(newValue) : newValue;
                } catch (e) {
                    console.error('Invalid data format:', e);
                    this._data = null;
                }
                break;
            case 'width':
                this._width = parseInt(newValue) || 600;
                break;
            case 'height':
                this._height = parseInt(newValue) || 400;
                break;
            case 'title':
                this._title = newValue || '';
                break;
        }

        if (this.shadowRoot.childNodes.length > 0) {
            this.render();
        }
    }

    // Public API method to set data programmatically
    setData(data) {
        this._data = data;
        this.render();
    }

    render() {
        // Clear previous content
        this.shadowRoot.innerHTML = '';

        // Create style element
        const style = document.createElement('style');
        style.textContent = `
            :host {
                display: block;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            }
            .chart-container {
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .chart-title {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
                color: #333;
            }
            .chart-svg {
                display: block;
            }
            .error-message {
                color: #d32f2f;
                padding: 16px;
                background: #ffebee;
                border-radius: 4px;
                border-left: 4px solid #d32f2f;
            }
            .axis {
                font-size: 12px;
            }
            .axis path,
            .axis line {
                stroke: #e0e0e0;
                shape-rendering: crispEdges;
            }
            .axis text {
                fill: #666;
            }
            .box {
                stroke: #2196F3;
                stroke-width: 2;
            }
            .median {
                stroke: #ff5722;
                stroke-width: 2;
            }
            .whisker {
                stroke: #666;
                stroke-width: 1.5;
            }
            .timeline-line {
                fill: none;
                stroke: #2196F3;
                stroke-width: 2;
            }
            .timeline-area {
                fill: #2196F3;
                opacity: 0.2;
            }
            .timeline-dot {
                fill: #2196F3;
                stroke: white;
                stroke-width: 2;
            }
            .grid line {
                stroke: #e0e0e0;
                stroke-opacity: 0.5;
                stroke-dasharray: 2,2;
            }
        `;

        // Create container
        const container = document.createElement('div');
        container.className = 'chart-container';

        // Add title if provided
        if (this._title) {
            const title = document.createElement('div');
            title.className = 'chart-title';
            title.textContent = this._title;
            container.appendChild(title);
        }

        this.shadowRoot.appendChild(style);
        this.shadowRoot.appendChild(container);

        // Render appropriate chart based on type
        if (!this._data) {
            this.renderError('No data provided');
            return;
        }

        try {
            if (this._type === 'boxplot') {
                this.renderBoxPlot(container);
            } else if (this._type === 'timeline') {
                this.renderTimeline(container);
            } else {
                this.renderError(`Unknown chart type: ${this._type}`);
            }
        } catch (e) {
            this.renderError(`Error rendering chart: ${e.message}`);
        }
    }

    renderError(message) {
        const error = document.createElement('div');
        error.className = 'error-message';
        error.textContent = message;
        this.shadowRoot.querySelector('.chart-container').appendChild(error);
    }

    /**
     * Render a box plot chart
     * Expected data format: 
     * [
     *   { label: 'Category 1', min: 10, q1: 20, median: 30, q3: 40, max: 50 },
     *   { label: 'Category 2', min: 15, q1: 25, median: 35, q3: 45, max: 55 }
     * ]
     */
    renderBoxPlot(container) {
        const margin = { top: 20, right: 30, bottom: 60, left: 60 };
        const width = this._width - margin.left - margin.right;
        const height = this._height - margin.top - margin.bottom;

        // Load D3 if not already loaded
        if (!window.d3) {
            this.renderError('D3.js library not loaded. Please include D3.js before using this component.');
            return;
        }

        const d3 = window.d3;

        // Create SVG
        const svg = d3.select(container)
            .append('svg')
            .attr('class', 'chart-svg')
            .attr('width', this._width)
            .attr('height', this._height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // X scale (categories)
        const x = d3.scaleBand()
            .range([0, width])
            .domain(this._data.map(d => d.label))
            .padding(0.4);

        // Y scale (values)
        const allValues = this._data.flatMap(d => [d.min, d.max]);
        const y = d3.scaleLinear()
            .domain([Math.min(...allValues) * 0.9, Math.max(...allValues) * 1.1])
            .range([height, 0]);

        // Add grid
        svg.append('g')
            .attr('class', 'grid')
            .call(d3.axisLeft(y)
                .tickSize(-width)
                .tickFormat(''));

        // Add X axis
        svg.append('g')
            .attr('class', 'axis axis-x')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x))
            .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end');

        // Add Y axis
        svg.append('g')
            .attr('class', 'axis axis-y')
            .call(d3.axisLeft(y));

        // Draw box plots
        const boxWidth = x.bandwidth();

        this._data.forEach(d => {
            const center = x(d.label) + boxWidth / 2;

            // Vertical line from min to max
            svg.append('line')
                .attr('class', 'whisker')
                .attr('x1', center)
                .attr('x2', center)
                .attr('y1', y(d.min))
                .attr('y2', y(d.max));

            // Box from Q1 to Q3
            svg.append('rect')
                .attr('class', 'box')
                .attr('x', x(d.label))
                .attr('y', y(d.q3))
                .attr('width', boxWidth)
                .attr('height', y(d.q1) - y(d.q3))
                .attr('fill', '#E3F2FD');

            // Median line
            svg.append('line')
                .attr('class', 'median')
                .attr('x1', x(d.label))
                .attr('x2', x(d.label) + boxWidth)
                .attr('y1', y(d.median))
                .attr('y2', y(d.median));

            // Min cap
            svg.append('line')
                .attr('class', 'whisker')
                .attr('x1', center - boxWidth / 4)
                .attr('x2', center + boxWidth / 4)
                .attr('y1', y(d.min))
                .attr('y2', y(d.min));

            // Max cap
            svg.append('line')
                .attr('class', 'whisker')
                .attr('x1', center - boxWidth / 4)
                .attr('x2', center + boxWidth / 4)
                .attr('y1', y(d.max))
                .attr('y2', y(d.max));
        });
    }

    /**
     * Render a timeline chart
     * Expected data format:
     * [
     *   { date: '2024-01-01', value: 100, label: 'Event 1' },
     *   { date: '2024-02-01', value: 150, label: 'Event 2' }
     * ]
     */
    renderTimeline(container) {
        const margin = { top: 20, right: 30, bottom: 60, left: 60 };
        const width = this._width - margin.left - margin.right;
        const height = this._height - margin.top - margin.bottom;

        if (!window.d3) {
            this.renderError('D3.js library not loaded. Please include D3.js before using this component.');
            return;
        }

        const d3 = window.d3;

        // Parse dates
        const data = this._data.map(d => ({
            ...d,
            date: new Date(d.date)
        }));

        // Create SVG
        const svg = d3.select(container)
            .append('svg')
            .attr('class', 'chart-svg')
            .attr('width', this._width)
            .attr('height', this._height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // X scale (time)
        const x = d3.scaleTime()
            .domain(d3.extent(data, d => d.date))
            .range([0, width]);

        // Y scale (values)
        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value) * 1.1])
            .range([height, 0]);

        // Add grid
        svg.append('g')
            .attr('class', 'grid')
            .call(d3.axisLeft(y)
                .tickSize(-width)
                .tickFormat(''));

        // Add area under the line
        const area = d3.area()
            .x(d => x(d.date))
            .y0(height)
            .y1(d => y(d.value))
            .curve(d3.curveMonotoneX);

        svg.append('path')
            .datum(data)
            .attr('class', 'timeline-area')
            .attr('d', area);

        // Add line
        const line = d3.line()
            .x(d => x(d.date))
            .y(d => y(d.value))
            .curve(d3.curveMonotoneX);

        svg.append('path')
            .datum(data)
            .attr('class', 'timeline-line')
            .attr('d', line);

        // Add dots
        svg.selectAll('.timeline-dot')
            .data(data)
            .enter()
            .append('circle')
            .attr('class', 'timeline-dot')
            .attr('cx', d => x(d.date))
            .attr('cy', d => y(d.value))
            .attr('r', 5)
            .append('title')
            .text(d => `${d.label || d.date.toLocaleDateString()}: ${d.value}`);

        // Add X axis
        svg.append('g')
            .attr('class', 'axis axis-x')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(x)
                .ticks(6)
                .tickFormat(d3.timeFormat('%b %d')))
            .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end');

        // Add Y axis
        svg.append('g')
            .attr('class', 'axis axis-y')
            .call(d3.axisLeft(y));
    }
}

// Register the custom element
customElements.define('lexmachina-chart', LexMachinaChart);

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LexMachinaChart;
}
