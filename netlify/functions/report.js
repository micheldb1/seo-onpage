// Netlify serverless function to handle report viewing
exports.handler = async (event, context) => {
  // Get the report ID from the query parameters
  const reportId = event.queryStringParameters.id;
  
  if (!reportId) {
    return {
      statusCode: 400,
      body: 'Report ID is required'
    };
  }
  
  // Since we can't access actual report files on Netlify,
  // we'll generate a demo report HTML
  const demoReportHtml = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEO Audit Report - Demo</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <style>
            body { font-family: Arial, sans-serif; }
            .report-header { background-color: #f8f9fa; padding: 20px; margin-bottom: 30px; }
            .score-card { text-align: center; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .score-good { background-color: #d4edda; color: #155724; }
            .score-warning { background-color: #fff3cd; color: #856404; }
            .score-error { background-color: #f8d7da; color: #721c24; }
            .factor-card { margin-bottom: 15px; border-radius: 5px; padding: 15px; }
            .pass { border-left: 5px solid #28a745; }
            .warning { border-left: 5px solid #ffc107; }
            .error { border-left: 5px solid #dc3545; }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="report-header">
                <h1 class="mb-4">On-Page SEO Audit Report</h1>
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>URL:</strong> ${event.queryStringParameters.url || 'example.com'}</p>
                        <p><strong>Report ID:</strong> ${reportId}</p>
                        <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <p><strong>Overall Score:</strong> 78%</p>
                        <p><strong>Total Checks:</strong> 45</p>
                    </div>
                </div>
            </div>

            <h2 class="mb-4">Summary</h2>
            <div class="row">
                <div class="col-md-4">
                    <div class="score-card score-warning">
                        <h3>78%</h3>
                        <p>Overall Score</p>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Technical SEO</h5>
                                    <div class="progress">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 85%" aria-valuenow="85" aria-valuemin="0" aria-valuemax="100">85%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Content SEO</h5>
                                    <div class="progress">
                                        <div class="progress-bar bg-warning" role="progressbar" style="width: 72%" aria-valuenow="72" aria-valuemin="0" aria-valuemax="100">72%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Structured Data</h5>
                                    <div class="progress">
                                        <div class="progress-bar bg-success" role="progressbar" style="width: 90%" aria-valuenow="90" aria-valuemin="0" aria-valuemax="100">90%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Link Analysis</h5>
                                    <div class="progress">
                                        <div class="progress-bar bg-warning" role="progressbar" style="width: 68%" aria-valuenow="68" aria-valuemin="0" aria-valuemax="100">68%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <h2 class="mt-5 mb-4">Detailed Findings</h2>
            <div class="accordion" id="reportAccordion">
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#technicalSEO">
                            Technical SEO (85%)
                        </button>
                    </h2>
                    <div id="technicalSEO" class="accordion-collapse collapse show" data-bs-parent="#reportAccordion">
                        <div class="accordion-body">
                            <div class="factor-card pass">
                                <h5>HTTP Status Code <span class="badge bg-success">Pass</span></h5>
                                <p>The page returns a 200 OK status code.</p>
                            </div>
                            <div class="factor-card pass">
                                <h5>SSL Implementation <span class="badge bg-success">Pass</span></h5>
                                <p>The site uses HTTPS with a valid SSL certificate.</p>
                            </div>
                            <div class="factor-card warning">
                                <h5>Page Load Speed <span class="badge bg-warning text-dark">Warning</span></h5>
                                <p>The page load time is 3.2 seconds. Aim for under 2 seconds for optimal performance.</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#contentSEO">
                            Content SEO (72%)
                        </button>
                    </h2>
                    <div id="contentSEO" class="accordion-collapse collapse" data-bs-parent="#reportAccordion">
                        <div class="accordion-body">
                            <div class="factor-card pass">
                                <h5>Title Tag <span class="badge bg-success">Pass</span></h5>
                                <p>The title tag is well-optimized and contains the primary keyword.</p>
                            </div>
                            <div class="factor-card warning">
                                <h5>Meta Description <span class="badge bg-warning text-dark">Warning</span></h5>
                                <p>The meta description is present but could be more compelling.</p>
                            </div>
                            <div class="factor-card error">
                                <h5>Content Length <span class="badge bg-danger">Error</span></h5>
                                <p>The content is only 300 words. Aim for at least 1,000 words for comprehensive coverage.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mt-5 text-center">
                <p class="text-muted">This is a demo report generated by the Onpage SEO Audit Tool</p>
                <p class="text-muted">Report ID: ${reportId}</p>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
  `;
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'text/html'
    },
    body: demoReportHtml
  };
};
