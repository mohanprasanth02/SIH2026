import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { MainLayout } from './components/layout/MainLayout';
import { Dashboard } from './pages/Dashboard';
import { Analysis } from './pages/Analysis';
import { ChangeDetection } from './pages/ChangeDetection';
import { OpticalSAR } from './pages/OpticalSAR';
import { LandCover } from './pages/LandCover';
import { Reports } from './pages/Reports';
import { Models } from './pages/Models';
import { Settings } from './pages/Settings';

import type { Transition } from 'framer-motion';

// Framer Motion page transition variants
const pageVariants = {
  initial: { opacity: 0, y: 10, scale: 0.995 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit:    { opacity: 0, scale: 0.998 },
};

const pageTransition: Transition = {
  duration: 0.22,
  ease: "easeInOut",
};

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        transition={pageTransition}
        className="h-full w-full"
      >
        <Routes location={location}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/change-detection" element={<ChangeDetection />} />
          <Route path="/optical-sar" element={<OpticalSAR />} />
          <Route path="/land-cover" element={<LandCover />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/models" element={<Models />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <MainLayout>
      <AnimatedRoutes />
    </MainLayout>
  );
}
