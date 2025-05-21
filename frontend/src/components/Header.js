import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import SecurityIcon from '@mui/icons-material/Security';

export const Header = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <SecurityIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AI HoneyPot System
        </Typography>
        <Box>
          <Button color="inherit" component={RouterLink} to="/">
            Alerts
          </Button>
          <Button color="inherit" component={RouterLink} to="/honeypots">
            Honeypots
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};
