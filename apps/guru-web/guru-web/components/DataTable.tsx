'use client';

/**
 * Data Table Component
 * Displays tabular data with glassmorphic styling
 */

import { motion } from 'framer-motion';

interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataTableProps {
  columns: Column[];
  data: any[];
  title?: string;
}

export default function DataTable({ columns, data, title }: DataTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="glass rounded-2xl p-8 border border-white/20">
        <p className="text-gray-500 dark:text-gray-400 text-center">No data available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl border border-white/20 overflow-hidden"
    >
      {title && (
        <div className="px-6 py-4 border-b border-white/10">
          <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200">{title}</h3>
        </div>
      )}
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-white/5">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className="px-6 py-4 text-left text-sm font-semibold text-gray-700 dark:text-gray-300"
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <motion.tr
                key={rowIndex}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: rowIndex * 0.05 }}
                className="border-b border-white/10 hover:bg-white/5 transition-smooth"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400"
                  >
                    {column.render
                      ? column.render(row[column.key], row)
                      : row[column.key] || '-'}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
}

