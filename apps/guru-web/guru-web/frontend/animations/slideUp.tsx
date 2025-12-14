/**
 * Slide Up Animation
 * Elements slide up from bottom with fade
 * Perfect for cards, modals, and content sections
 */

import { motion } from 'framer-motion';

export const slideUp = {
  initial: { opacity: 0, y: 60 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 60 },
};

export const slideUpVariants = {
  hidden: { 
    opacity: 0, 
    y: 60,
  },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.6,
      ease: 'easeInOut',
    }
  },
};

// Component wrapper for slide-up
interface SlideUpProps {
  children: React.ReactNode;
  delay?: number;
  duration?: number;
}

export const SlideUp = ({ children, delay = 0, duration = 0.6 }: SlideUpProps) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0, y: 60 },
        visible: {
          opacity: 1,
          y: 0,
          transition: {
            delay,
            duration,
            ease: [0.4, 0, 0.2, 1] as const,
          }
        }
      }}
    >
      {children}
    </motion.div>
  );
};

