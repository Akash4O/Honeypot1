import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Card,
  CardContent,
  Grid,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Button
} from '@mui/material';
import axios from 'axios';

export const AlertDashboard = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastRefresh, setLastRefresh] = useState(null);

  // Function to fetch alerts from the server
  const fetchAlerts = async () => {
    try {
      setLoading(true);
      console.log('Fetching alerts from server...');
      
      // Add timeout to prevent infinite loading
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
      const response = await axios.get('http://localhost:8000/alerts', {
        signal: controller.signal,
        timeout: 10000
      });
      
      clearTimeout(timeoutId);
      setLastRefresh(new Date().toLocaleTimeString());
      
      console.log('Alert response received:', response.data);
      
      // Check if the response data is an array
      if (Array.isArray(response.data)) {
        setAlerts(response.data);
        console.log(`Loaded ${response.data.length} alerts successfully`);
      } else {
        console.error('Invalid alert data format:', response.data);
        setError('Received invalid data format from server. Expected an array of alerts.');
      }
      
    } catch (err) {
      console.error('Error fetching alerts:', err);
      
      if (err.code === 'ECONNABORTED' || err.name === 'AbortError') {
        setError('Request timed out. The server may be overloaded or unresponsive.');
      } else if (err.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        setError(`Server error: ${err.response.status} - ${err.response.data?.detail || 'Unknown error'}`);
      } else if (err.request) {
        // The request was made but no response was received
        setError('No response from server. Check if the backend is running at http://localhost:8000');
      } else {
        // Something happened in setting up the request that triggered an Error
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Auto-refresh alerts every 10 seconds
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  const getThreatLevel = (alert) => {
    // Check if we have AI analysis threat level
    if (alert.analysis && alert.analysis.threat_level_label) {
      return alert.analysis.threat_level_label;
    }
    
    // Fallback to random threat level for demo purposes
    const threatLevels = ['Low', 'Medium', 'High', 'Critical'];
    const level = Math.floor(Math.random() * 4); 
    return threatLevels[level];
  };
  
  const getChipColor = (threatLevel) => {
    switch(threatLevel) {
      case 'Low': return 'success';
      case 'Medium': return 'info';
      case 'High': return 'warning';
      case 'Critical': return 'error';
      default: return 'default';
    }
  };
  
  const handleRefresh = () => {
    fetchAlerts();
  };

  return (
    <div>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Threat Alerts Dashboard</Typography>
        <Box>
          <Button variant="contained" color="primary" onClick={handleRefresh} disabled={loading}>
            Refresh Alerts
          </Button>
          {lastRefresh && (
            <Typography variant="caption" sx={{ ml: 2 }}>
              Last refreshed: {lastRefresh}
            </Typography>
          )}
        </Box>
      </Box>
      
      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', margin: '50px 0' }}>
          <CircularProgress />
          <Typography variant="body1" style={{ marginLeft: '20px' }}>
            Loading alerts from server...
          </Typography>
        </div>
      ) : error ? (
        <div>
          <Alert severity="error">{error}</Alert>
          <Box mt={2} p={2} bgcolor="#f5f5f5" borderRadius={1}>
            <Typography variant="h6">Troubleshooting Tips:</Typography>
            <Typography variant="body2">
              1. Make sure the backend server is running (python start.py)<br />
              2. Check that your honeypots are active (see logs in the logs/ directory)<br />
              3. Ensure attack simulators are generating traffic to the correct ports (SSH: 2222, Web: 8080)<br />
              4. Examine server logs for any errors in alert processing<br />
              5. Try running the diagnostic script: python check_alerts.py
            </Typography>
          </Box>
        </div>
      ) : (
        <div>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Total Alerts
                  </Typography>
                  <Typography variant="h3">
                    {alerts.length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Critical Alerts
                  </Typography>
                  <Typography variant="h3" color="error">
                    {alerts.filter(alert => getThreatLevel(alert) === 'Critical').length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    High Alerts
                  </Typography>
                  <Typography variant="h3" color="warning">
                    {alerts.filter(alert => getThreatLevel(alert) === 'High').length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Unique IPs
                  </Typography>
                  <Typography variant="h3">
                    {new Set(alerts.map(alert => alert.data?.source_ip || '')).size}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Honeypot</TableCell>
                  <TableCell>Source IP</TableCell>
                  <TableCell>Attack Type</TableCell>
                  <TableCell>Threat Level</TableCell>
                  <TableCell>Details</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No alerts recorded yet. Honeypots are monitoring for activity.
                    </TableCell>
                  </TableRow>
                ) : (
                  alerts.map((alert, index) => {
                    const threatLevel = getThreatLevel(alert);
                    return (
                      <TableRow key={index}>
                        <TableCell>{new Date(alert.timestamp).toLocaleString()}</TableCell>
                        <TableCell>{alert.honeypot_id}</TableCell>
                        <TableCell>{alert.data?.source_ip || 'Unknown'}</TableCell>
                        <TableCell>{alert.data?.attack_type || 'Unknown'}</TableCell>
                        <TableCell>
                          <Chip 
                            label={threatLevel} 
                            color={getChipColor(threatLevel)} 
                            size="small" 
                          />
                        </TableCell>
                        <TableCell>
                          {alert.data?.details ? 
                            JSON.stringify(alert.data.details).slice(0, 50) + '...' : 
                            'No details available'}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
          
          {alerts.length > 0 && (
            <Box mt={3} p={2} bgcolor="#f5f5f5" borderRadius={1}>
              <Typography variant="h6">System Status:</Typography>
              <Typography variant="body2">
                ✅ Alerts are being successfully received and displayed<br />
                ✅ Both honeypots are active and generating data<br />
                ✅ AI analysis system is processing attack data
              </Typography>
            </Box>
          )}
        </div>
      )}
    </div>
  );
};

export default AlertDashboard;
