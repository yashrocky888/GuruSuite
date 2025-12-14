/**
 * Slide Left Animation
 * Elements slide in from the right
 * Great for sidebars, navigation, and sequential content
 */

import { motion } from 'framer-motion';

export const slideLeft = {
  initial: { opacity: 0, x: 100 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -100 },
};

export const slideLeftVariants = {
  hidden: { 
    opacity: 0, 
    x: 100,
  },
  visible: { 
    opacity: 1, 
    x: 0,
    transition: {
      duration: 0.5,
      ease: [0.4, 0, 0.2, 1],
    }
  },
};

// Component wrapper for slide-left
export const SlideLeft = ({ children, delay = 0, duration = 0.5 }) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0, x: 100 },
        visible: {
          opacity: 1,
          x: 0,
          transition: {
            delay,
            duration,
            ease: [0.4, 0, 0.2, 1],
          }
        }
      }}
    >
      {children}
    </motion.div>
  );
};

