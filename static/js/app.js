document.addEventListener('DOMContentLoaded', function() {

    const API_URL = '/api/stats';
    let verdictChart = null;
    let trendChart = null;

    function formatVerdict(verdict) {
        // Just return the verdict string which already contains an emoji
        return verdict;
    }

    function updateSummary(data) {
        const totalTriggersEl = document.getElementById('total-triggers');
        if (totalTriggersEl) {
            totalTriggersEl.textContent = data.total_triggers;
        }
    }

    function updateActivityFeed(data) {
        const activityFeedEl = document.getElementById('activity-feed');
        if (!activityFeedEl) return;

        activityFeedEl.innerHTML = ''; // Clear existing items

        if (data.recent_triggers && data.recent_triggers.length > 0) {
            data.recent_triggers.reverse().forEach(trigger => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                const subredditLink = `<a href="https://www.reddit.com/r/${trigger.subreddit}" target="_blank">r/${trigger.subreddit}</a>`;
                li.innerHTML = `${trigger.timestamp} - ${formatVerdict(trigger.verdict)} in ${subredditLink}`;
                activityFeedEl.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = 'No recent activity found.';
            activityFeedEl.appendChild(li);
        }
    }

    function updateSubredditList(data) {
        const subredditListEl = document.getElementById('subreddit-list');
        if (!subredditListEl) return;

        subredditListEl.innerHTML = ''; // Clear existing items
        const activity = data.subreddit_activity;

        if (activity && Object.keys(activity).length > 0) {
            for (const [subreddit, count] of Object.entries(activity)) {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                const subredditLink = `<a href="https://www.reddit.com/r/${subreddit}" target="_blank">r/${subreddit}</a>`;
                li.innerHTML = `${subredditLink} <span class="badge bg-primary rounded-pill">${count}</span>`;
                subredditListEl.appendChild(li);
            }
        } else {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = 'No subreddit data yet.';
            subredditListEl.appendChild(li);
        }
    }

    function updateChart(data) {
        const ctx = document.getElementById('verdict-chart');
        if (!ctx) return;

        const distribution = data.verdict_distribution;
        const labels = Object.keys(distribution);
        const chartData = Object.values(distribution);
        
        const backgroundColors = [
            'rgba(40, 167, 69, 0.7)',  // Green
            'rgba(255, 193, 7, 0.7)',   // Yellow
            'rgba(220, 53, 69, 0.7)'    // Red
        ];

        if (verdictChart) {
            // Update existing chart
            verdictChart.data.labels = labels;
            verdictChart.data.datasets[0].data = chartData;
            verdictChart.update();
        } else {
            // Create new chart
            verdictChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Verdict Distribution',
                        data: chartData,
                        backgroundColor: backgroundColors,
                        borderColor: backgroundColors.map(c => c.replace('0.7', '1')),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        }
    }

    function updateTrendChart(data) {
        const ctx = document.getElementById('trend-chart');
        if (!ctx) return;

        const trends = data.verdict_trends;
        if (!trends || !trends.labels || trends.labels.length === 0) {
            ctx.parentElement.innerHTML = '<p class="text-center text-muted">Not enough data for a trend chart yet.</p>';
            return;
        }

        const datasets = [
            {
                label: '🔴 Potentially AI-Generated',
                data: trends.datasets['🔴 Potentially AI-Generated'],
                borderColor: 'rgba(220, 53, 69, 1)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                fill: true,
                tension: 0.1
            },
            {
                label: '🟡 Possibly AI-Generated',
                data: trends.datasets['🟡 Possibly AI-Generated'],
                borderColor: 'rgba(255, 193, 7, 1)',
                backgroundColor: 'rgba(255, 193, 7, 0.1)',
                fill: true,
                tension: 0.1
            },
            {
                label: '🟢 Likely Human',
                data: trends.datasets['🟢 Likely Human'],
                borderColor: 'rgba(40, 167, 69, 1)',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.1
            }
        ];

        if (trendChart) {
            trendChart.data.labels = trends.labels;
            trendChart.data.datasets = datasets;
            trendChart.update();
        } else {
            trendChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trends.labels,
                    datasets: datasets
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                // Ensure only whole numbers are used for ticks
                                precision: 0
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    }
                }
            });
        }
    }

    async function fetchData() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            updateSummary(data);
            updateChart(data);
            updateActivityFeed(data);
            updateSubredditList(data);
            updateTrendChart(data);

        } catch (error) {
            console.error("Could not fetch data:", error);
        }
    }

    // Fetch data on page load
    fetchData();

    // Refresh data every 30 seconds
    setInterval(fetchData, 30000);

});
