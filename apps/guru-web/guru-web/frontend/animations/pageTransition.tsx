/**
 * Page Transition Animation
 * Smooth transitions between pages
 * Used in Next.js App Router for route changes
 */

import { motion } from 'framer-motion';

export const pageTransition = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
  },
  exit: { 
    opacity: 0, 
    y: -20,
  },
};

export const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
  },
  exit: {
    opacity: 0,
    y: -20,
  },
};

// Page transition wrapper component
interface PageTransitionProps {
  children: React.ReactNode;
}

export const PageTransition = ({ children }: PageTransitionProps) => {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={pageVariants}
      transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] as const }}
    >
      {children}
    </motion.div>
  );
};
