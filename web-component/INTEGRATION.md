# Web Component Integration

This directory contains a standalone web component for visualizing legal data from the Lex Machina A2A Agent.

## Quick Start

### 1. Include Dependencies

```html
<!-- Include D3.js (required dependency) -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- Include the LexMachina Chart component -->
<script src="web-component/src/lexmachina-chart.js"></script>
```

### 2. Use the Component

```html
<!-- Box Plot -->
<lexmachina-chart 
    type="boxplot"
    title="Case Duration by Court"
    width="800"
    height="500">
</lexmachina-chart>

<!-- Timeline Chart -->
<lexmachina-chart 
    type="timeline"
    title="Cases Filed Over Time"
    width="800"
    height="400">
</lexmachina-chart>
```

### 3. Set Data Programmatically

```javascript
const chart = document.querySelector('lexmachina-chart');

// For box plots
chart.setData([
    {
        label: 'SDNY',
        min: 30,
        q1: 120,
        median: 180,
        q3: 270,
        max: 450
    }
]);

// For timelines
chart.setData([
    {
        date: '2024-01-01',
        value: 45,
        label: 'January'
    }
]);
```

## Integration with Lex Machina Agent

The web component is designed to work seamlessly with the Lex Machina A2A Agent API running on `http://localhost:10011`.

### Example Integration

```javascript
async function visualizeAgentData(query) {
    // 1. Query the agent
    const response = await fetch('http://localhost:10011/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });
    
    const data = await response.json();
    
    // 2. Transform the data
    const chartData = transformToChartFormat(data);
    
    // 3. Update the chart
    const chart = document.querySelector('lexmachina-chart');
    chart.setData(chartData);
}

// Transform API response to box plot format
function transformToChartFormat(apiData) {
    // Example transformation logic
    return apiData.results.map(item => ({
        label: item.court,
        min: item.stats.min_duration,
        q1: item.stats.q1_duration,
        median: item.stats.median_duration,
        q3: item.stats.q3_duration,
        max: item.stats.max_duration
    }));
}
```

## Files

- **`src/lexmachina-chart.js`** - Main component (410 lines)
- **`examples/`** - Three working HTML examples
  - `boxplot-example.html` - Interactive box plot demo
  - `timeline-example.html` - Interactive timeline demo
  - `integration-example.html` - Full integration with API
  - `demo.html` - Overview and documentation
- **`tests/test.html`** - Browser-based test suite
- **`README.md`** - Comprehensive documentation
- **`package.json`** - NPM package configuration

## Features

✅ Framework-agnostic (works with React, Angular, Vue, or plain HTML)  
✅ Shadow DOM for CSS encapsulation  
✅ D3.js-powered visualizations  
✅ Two chart types: Box plots and Timeline charts  
✅ Fully documented with examples  
✅ Browser-based test suite  

## Browser Support

- Chrome/Edge 79+
- Firefox 63+
- Safari 13+
- Opera 66+

Requires Custom Elements v1 and Shadow DOM v1 support.

## License

Apache-2.0 (same as parent project)
