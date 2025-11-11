# LexMachina Chart Web Component

A standalone, framework-agnostic web component for displaying **box plots** and **timing line charts** using D3.js. This component can be used with any JavaScript framework (React, Angular, Vue, etc.) or vanilla JavaScript/HTML.

## Features

- 🎨 **Two Chart Types**: Box plots for statistical distributions and timeline charts for temporal data
- 🔌 **Framework Agnostic**: Works with React, Angular, Vue, or plain HTML
- 📦 **Standalone Module**: No build step required, just include and use
- 🎯 **Custom Element**: Uses Web Components standard (Custom Elements v1)
- 🎭 **Shadow DOM**: Encapsulated styles, no CSS conflicts
- 📊 **D3.js Powered**: Leverages D3.js for professional data visualizations
- 🔧 **Customizable**: Control size, colors, and data via attributes or JavaScript API

## Installation

### Option 1: Direct Include (Recommended for quick start)

```html
<!-- Include D3.js first -->
<script src="https://d3js.org/d3.v7.min.js"></script>

<!-- Include the component -->
<script src="path/to/lexmachina-chart.js"></script>
```

### Option 2: NPM/Module Import (For bundled projects)

```bash
npm install d3
```

```javascript
import 'd3';
import './path/to/lexmachina-chart.js';
```

## Usage

### Basic HTML Usage

#### Box Plot Example

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="lexmachina-chart.js"></script>
</head>
<body>
    <lexmachina-chart 
        type="boxplot"
        title="Case Duration Distribution by Court"
        width="800"
        height="500"
        data='[
            {
                "label": "SDNY",
                "min": 30,
                "q1": 120,
                "median": 180,
                "q3": 270,
                "max": 450
            },
            {
                "label": "NDCA",
                "min": 45,
                "q1": 140,
                "median": 210,
                "q3": 310,
                "max": 500
            },
            {
                "label": "CDCA",
                "min": 60,
                "q1": 150,
                "median": 220,
                "q3": 320,
                "max": 480
            }
        ]'>
    </lexmachina-chart>
</body>
</html>
```

#### Timeline Chart Example

```html
<lexmachina-chart 
    type="timeline"
    title="Cases Filed Over Time"
    width="800"
    height="400"
    data='[
        {
            "date": "2024-01-01",
            "value": 45,
            "label": "January"
        },
        {
            "date": "2024-02-01",
            "value": 52,
            "label": "February"
        },
        {
            "date": "2024-03-01",
            "value": 68,
            "label": "March"
        },
        {
            "date": "2024-04-01",
            "value": 71,
            "label": "April"
        },
        {
            "date": "2024-05-01",
            "value": 63,
            "label": "May"
        }
    ]'>
</lexmachina-chart>
```

### JavaScript API Usage

```javascript
// Create element
const chart = document.createElement('lexmachina-chart');

// Set attributes
chart.setAttribute('type', 'boxplot');
chart.setAttribute('title', 'My Chart');
chart.setAttribute('width', '800');
chart.setAttribute('height', '500');

// Set data programmatically (preferred for dynamic data)
chart.setData([
    {
        label: 'Category A',
        min: 10,
        q1: 25,
        median: 40,
        q3: 60,
        max: 90
    },
    {
        label: 'Category B',
        min: 15,
        q1: 30,
        median: 45,
        q3: 65,
        max: 95
    }
]);

// Append to DOM
document.body.appendChild(chart);
```

## Framework Integration

### React

```jsx
import React, { useEffect, useRef } from 'react';
import 'd3';
import '../path/to/lexmachina-chart.js';

function BoxPlotChart({ data, title }) {
    const chartRef = useRef(null);

    useEffect(() => {
        if (chartRef.current && data) {
            chartRef.current.setData(data);
        }
    }, [data]);

    return (
        <lexmachina-chart
            ref={chartRef}
            type="boxplot"
            title={title}
            width="800"
            height="500"
        />
    );
}

export default BoxPlotChart;
```

### Angular

```typescript
import { Component, Input, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import 'd3';
import '../path/to/lexmachina-chart.js';

@Component({
    selector: 'app-chart',
    template: `
        <lexmachina-chart
            #chart
            [attr.type]="type"
            [attr.title]="title"
            [attr.width]="width"
            [attr.height]="height">
        </lexmachina-chart>
    `
})
export class ChartComponent implements AfterViewInit {
    @Input() type = 'boxplot';
    @Input() title = '';
    @Input() width = 600;
    @Input() height = 400;
    @Input() data: any[] = [];
    @ViewChild('chart') chartElement!: ElementRef;

    ngAfterViewInit() {
        this.updateChart();
    }

    ngOnChanges() {
        this.updateChart();
    }

    updateChart() {
        if (this.chartElement && this.chartElement.nativeElement) {
            (this.chartElement.nativeElement as any).setData(this.data);
        }
    }
}
```

### Vue

```vue
<template>
    <lexmachina-chart
        ref="chart"
        :type="type"
        :title="title"
        :width="width"
        :height="height"
    />
</template>

<script>
import 'd3';
import '../path/to/lexmachina-chart.js';

export default {
    name: 'ChartComponent',
    props: {
        type: { type: String, default: 'boxplot' },
        title: { type: String, default: '' },
        width: { type: Number, default: 600 },
        height: { type: Number, default: 400 },
        data: { type: Array, required: true }
    },
    watch: {
        data: {
            handler(newData) {
                if (this.$refs.chart) {
                    this.$refs.chart.setData(newData);
                }
            },
            deep: true,
            immediate: true
        }
    }
};
</script>
```

## Data Formats

### Box Plot Data Format

Box plots require statistical summary data with five-number summary for each category:

```javascript
[
    {
        "label": "Category Name",  // Category label (shown on x-axis)
        "min": 10,                 // Minimum value (lower whisker)
        "q1": 25,                  // First quartile (25th percentile)
        "median": 40,              // Median (50th percentile)
        "q3": 60,                  // Third quartile (75th percentile)
        "max": 90                  // Maximum value (upper whisker)
    },
    // ... more categories
]
```

**Use Cases for Box Plots:**
- Time to trial distributions by court
- Settlement amount distributions by case type
- Attorney experience levels across different firms
- Case duration comparisons

### Timeline Data Format

Timeline charts require time-series data with dates and values:

```javascript
[
    {
        "date": "2024-01-01",      // Date in ISO format (YYYY-MM-DD)
        "value": 45,               // Numeric value
        "label": "Event Label"     // Optional label for tooltips
    },
    // ... more data points
]
```

**Use Cases for Timeline Charts:**
- Cases filed over time
- Settlement amounts trend
- Judge decisions per month
- Motion grant rates over time

## Attributes

| Attribute | Type   | Default    | Description                                    |
|-----------|--------|------------|------------------------------------------------|
| `type`    | String | 'boxplot'  | Chart type: 'boxplot' or 'timeline'            |
| `data`    | JSON   | null       | Chart data (JSON string or set via JavaScript) |
| `width`   | Number | 600        | Chart width in pixels                          |
| `height`  | Number | 400        | Chart height in pixels                         |
| `title`   | String | ''         | Chart title (optional)                         |

## Methods

### `setData(data)`

Programmatically set chart data. This is the preferred method for dynamic data updates.

```javascript
const chart = document.querySelector('lexmachina-chart');
chart.setData([...newData]);
```

## Styling

The component uses Shadow DOM for style encapsulation. All styles are scoped to the component and won't affect your page styles.

### Customization

To customize the appearance, you can modify the styles in the source file or use CSS custom properties (CSS variables) - though the current version uses inline styles for maximum compatibility.

## Browser Support

- ✅ Chrome/Edge 79+
- ✅ Firefox 63+
- ✅ Safari 13+
- ✅ Opera 66+

The component uses:
- Custom Elements v1 (Web Components)
- Shadow DOM v1
- ES6 Classes

## Integration with Lex Machina Agent

This component is designed to work seamlessly with the Lex Machina A2A Agent API. The agent can provide search suggestions and analytics data that can be visualized using this component.

Example workflow:
1. Query the Lex Machina agent for case statistics
2. Transform the response data into box plot or timeline format
3. Display the data using the web component

```javascript
// Fetch data from Lex Machina agent
async function fetchAndVisualize(query) {
    const response = await fetch('http://localhost:10011/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
    });
    
    const data = await response.json();
    
    // Transform data for visualization
    const chartData = transformToBoxPlot(data);
    
    // Update chart
    const chart = document.querySelector('lexmachina-chart');
    chart.setData(chartData);
}
```

## Development

### Running Examples

Open any HTML file in the `examples/` directory in a web browser. Make sure D3.js is loaded from CDN or locally.

### Testing

The component can be tested in any modern browser's developer console:

```javascript
// Create and test the component
const chart = document.createElement('lexmachina-chart');
chart.setAttribute('type', 'boxplot');
chart.setData([
    { label: 'Test', min: 0, q1: 25, median: 50, q3: 75, max: 100 }
]);
document.body.appendChild(chart);
```

## License

Apache-2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/LexMachinaInc/lexmachina-agent/issues).
