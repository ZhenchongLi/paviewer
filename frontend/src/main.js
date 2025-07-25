import { createChart } from 'lightweight-charts';
import './style.css';

const chartContainer = document.getElementById('chart-container');

const chart = createChart(chartContainer, {
    width: chartContainer.clientWidth,
    height: chartContainer.clientHeight,
    layout: {
        backgroundColor: '#ffffff',
        textColor: '#333',
    },
    grid: {
        vertLines: {
            color: '#eeeeee',
        },
        horzLines: {
            color: '#eeeeee',
        },
    },
    crosshair: {
        mode: 0,
    },
    rightPriceScale: {
        borderColor: '#cccccc',
    },
    timeScale: {
        borderColor: '#cccccc',
    },
});

const candlestickSeries = chart.addCandlestickSeries({
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
});

// Add sample data to see the chart
const sampleData = [
    { time: '2023-12-01', open: 100, high: 110, low: 95, close: 105 },
    { time: '2023-12-02', open: 105, high: 115, low: 100, close: 108 },
    { time: '2023-12-03', open: 108, high: 112, low: 102, close: 106 },
    { time: '2023-12-04', open: 106, high: 118, low: 104, close: 115 },
    { time: '2023-12-05', open: 115, high: 120, low: 110, close: 112 },
];

candlestickSeries.setData(sampleData);

// Add EMA20 line
const emaLineSeries = chart.addLineSeries({
    color: '#2196F3',
    lineWidth: 2,
});

const emaData = [
    { time: '2023-12-01', value: 102 },
    { time: '2023-12-02', value: 103 },
    { time: '2023-12-03', value: 104 },
    { time: '2023-12-04', value: 107 },
    { time: '2023-12-05', value: 110 },
];

emaLineSeries.setData(emaData);

window.addEventListener('resize', () => {
    chart.applyOptions({ 
        width: chartContainer.clientWidth, 
        height: chartContainer.clientHeight 
    });
});

console.log('PAViewer frontend initialized with sample data');