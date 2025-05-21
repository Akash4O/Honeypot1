import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Paper, 
  Card, 
  CardContent, 
  Grid, 
  Box,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  FormControlLabel
} from '@mui/material';
import axios from 'axios';

export const HoneypotDashboard = () => {
  const [honeypots, setHoneypots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchHoneypots = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/honeypots');
        setHoneypots(Object.entries(response.data).map(([id, data]) => ({
          id,
          ...data
        })));
        setLoading(false);
      } catch (err) {
        console.error('Error fetching honeypots:', err);
        setError('Failed to fetch honeypots. Server might not be running.');
        setLoading(false);
      }
    };
    
    fetchHoneypots();
    const interval = setInterval(fetchHoneypots, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  // Mock honeypots for demonstration when none are available
  const mockHoneypots = [
    { 
      id: 'ssh-honeypot-1', 
      type: 'SSH', 
      status: 'Active', 
      ip: '192.168.1.10', 
      port: 22, 
      connections: 15, 
      last_activity: new Date().toISOString() 
    },
    { 
      id: 'web-honeypot-1', 
      type: 'Web Server', 
      status: 'Active', 
      ip: '192.168.1.11', 
      port: 80, 
      connections: 32, 
      last_activity: new Date().toISOString() 
    },
    { 
      id: 'ftp-honeypot-1', 
      type: 'FTP', 
      status: 'Inactive', 
      ip: '192.168.1.12', 
      port: 21, 
      connections: 5, 
      last_activity: new Date(Date.now() - 86400000).toISOString() 
    },
    { 
      id: 'smb-honeypot-1', 
      type: 'SMB', 
      status: 'Active', 
      ip: '192.168.1.13', 
      port: 445, 
      connections: 8, 
      last_activity: new Date().toISOString() 
    }
  ];
  
  const displayHoneypots = honeypots.length > 0 ? honeypots : mockHoneypots;
  
  const toggleHoneypotStatus = (id) => {
    setHoneypots(prev => 
      prev.map(hp => 
        hp.id === id ? {...hp, status: hp.status === 'Active' ? 'Inactive' : 'Active'} : hp
      )
    );
  };
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }
  
  const activeHoneypots = displayHoneypots.filter(hp => hp.status === 'Active').length;
  const totalConnections = displayHoneypots.reduce((sum, hp) => sum + (hp.connections || 0), 0);
  
  return (
    <div>
      <Typography variant="h4" gutterBottom>
        Honeypot Management Dashboard
      </Typography>
      
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Honeypots
              </Typography>
              <Typography variant="h3">
                {displayHoneypots.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Honeypots
              </Typography>
              <Typography variant="h3" color="success.main">
                {activeHoneypots}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Inactive Honeypots
              </Typography>
              <Typography variant="h3" color="error.main">
                {displayHoneypots.length - activeHoneypots}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Connections
              </Typography>
              <Typography variant="h3">
                {totalConnections}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="contained" color="primary">
          Deploy New Honeypot
        </Button>
      </Box>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Port</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Connections</TableCell>
              <TableCell>Last Activity</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {displayHoneypots.map((honeypot) => (
              <TableRow key={honeypot.id}>
                <TableCell>{honeypot.id}</TableCell>
                <TableCell>{honeypot.type}</TableCell>
                <TableCell>{honeypot.ip}</TableCell>
                <TableCell>{honeypot.port}</TableCell>
                <TableCell>
                  <Chip 
                    label={honeypot.status} 
                    color={honeypot.status === 'Active' ? 'success' : 'error'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell>{honeypot.connections}</TableCell>
                <TableCell>{new Date(honeypot.last_activity).toLocaleString()}</TableCell>
                <TableCell>
                  <FormControlLabel
                    control={
                      <Switch 
                        checked={honeypot.status === 'Active'}
                        onChange={() => toggleHoneypotStatus(honeypot.id)}
                        color="primary"
                      />
                    }
                    label=""
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};
