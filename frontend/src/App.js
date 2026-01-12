/**
 *Contains the front end of the system that will display all the changes that the backend incorperates for the user
 */
import React, { useState, useEffect } from 'react';
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, Target, Activity, Plus, RefreshCw } from 'lucide-react';

const API_URL = 'http://localhost:5000/api';
const PORTFOLIO_ID = 'portfolio_123';

const PortfolioDashboard = () => {
  const [summary, setSummary] = useState(null);
  const [performance, setPerformance] = useState([]);
  const [allocation, setAllocation] = useState({ by_sector: [] });
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [newTransaction, setNewTransaction] = useState({
    ticker: '',
    shares: '',
    purchase_date: '',
    purchase_price: ''
  });

  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [summaryRes, performanceRes, allocationRes, transactionsRes] = await Promise.all([
        fetch(`${API_URL}/portfolio/${PORTFOLIO_ID}/summary`),
        fetch(`${API_URL}/portfolio/${PORTFOLIO_ID}/performance?start_date=2024-01-01`),
        fetch(`${API_URL}/portfolio/${PORTFOLIO_ID}/allocation`),
        fetch(`${API_URL}/portfolio/${PORTFOLIO_ID}/transactions`)
      ]);

      const summaryData = await summaryRes.json();
      const performanceData = await performanceRes.json();
      const allocationData = await allocationRes.json();
      const transactionsData = await transactionsRes.json();

      setSummary(summaryData);
      
      if (performanceData.dates && performanceData.values) {
        const chartData = performanceData.dates.map((date, idx) => ({
          date: date,
          value: performanceData.values[idx]
        }));
        setPerformance(chartData);
      }

      setAllocation(allocationData);
      setTransactions(transactionsData.transactions || []);
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load portfolio data. Make sure your backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddTransaction = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_URL}/portfolio/${PORTFOLIO_ID}/transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTransaction)
      });

      if (response.ok) {
        setNewTransaction({ ticker: '', shares: '', purchase_date: '', purchase_price: '' });
        setShowForm(false);
        fetchAllData();
      } else {
        const errorData = await response.json();
        alert('Error adding transaction: ' + JSON.stringify(errorData));
      }
    } catch (err) {
      console.error('Error adding transaction:', err);
      alert('Failed to add transaction');
    }
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading portfolio data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="bg-white rounded-xl shadow-sm p-8 max-w-md border border-gray-200">
          <h2 className="text-xl font-semibold text-red-600 mb-3">Connection Error</h2>
          <p className="text-gray-600 text-sm mb-4">{error}</p>
          <button 
            onClick={fetchAllData}
            className="w-full bg-blue-600 text-white py-2.5 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Portfolio Analytics</h1>
              <p className="text-sm text-gray-500 mt-1">Real-time investment tracking and analysis</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="flex items-center gap-2 bg-blue-600 text-white px-5 py-2.5 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shadow-sm"
            >
              <Plus className="w-4 h-4" />
              Add Transaction
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* Add Transaction Form */}
        {showForm && (
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Add New Transaction</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1.5">Ticker</label>
                <input
                  type="text"
                  placeholder="AAPL"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  value={newTransaction.ticker}
                  onChange={(e) => setNewTransaction({...newTransaction, ticker: e.target.value.toUpperCase()})}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1.5">Shares</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="10"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  value={newTransaction.shares}
                  onChange={(e) => setNewTransaction({...newTransaction, shares: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1.5">Purchase Date</label>
                <input
                  type="date"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  value={newTransaction.purchase_date}
                  onChange={(e) => setNewTransaction({...newTransaction, purchase_date: e.target.value})}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1.5">Purchase Price</label>
                <input
                  type="number"
                  step="0.01"
                  placeholder="150.00"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  value={newTransaction.purchase_price}
                  onChange={(e) => setNewTransaction({...newTransaction, purchase_price: e.target.value})}
                  required
                />
              </div>
            </div>
            <div className="flex gap-3 mt-4">
              <button
                onClick={handleAddTransaction}
                className="bg-blue-600 text-white py-2 px-5 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Add Transaction
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="bg-gray-100 text-gray-700 py-2 px-5 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <SummaryCard
            title="Total Value"
            value={summary?.total_value || 0}
            icon={<DollarSign className="w-5 h-5" />}
            format="currency"
            color="blue"
          />
          <SummaryCard
            title="Total Return"
            value={summary?.total_return || 0}
            icon={<TrendingUp className="w-5 h-5" />}
            format="currency"
            change={summary?.total_return_percent || 0}
            color="green"
          />
          <SummaryCard
            title="Positions"
            value={summary?.num_positions || 0}
            icon={<Target className="w-5 h-5" />}
            color="purple"
          />
          <SummaryCard
            title="Total Invested"
            value={summary?.total_cost || 0}
            icon={<Activity className="w-5 h-5" />}
            format="currency"
            color="orange"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Performance Chart */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Portfolio Performance</h2>
            {performance.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tick={{fontSize: 11, fill: '#6b7280'}}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{fontSize: 11, fill: '#6b7280'}} />
                  <Tooltip 
                    formatter={(value) => `$${Number(value).toFixed(2)}`}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#3B82F6" 
                    strokeWidth={2} 
                    dot={false}
                    name="Portfolio Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
                No performance data available. Add transactions to see your portfolio growth!
              </div>
            )}
          </div>

          {/* Sector Allocation Pie Chart */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-lg font-semibold mb-4 text-gray-900">Sector Allocation</h2>
            {allocation.by_sector && allocation.by_sector.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={allocation.by_sector}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${percent.toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {allocation.by_sector.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value) => `$${Number(value).toFixed(2)}`}
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
                No sector data available
              </div>
            )}
          </div>
        </div>

        {/* Holdings Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 pb-0">
            <h2 className="text-lg font-semibold text-gray-900">Current Holdings</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticker</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Cost</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gain/Loss</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Weight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {summary?.positions && summary.positions.length > 0 ? (
                  summary.positions.map((position, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 text-sm font-semibold text-blue-600">{position.ticker}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{position.shares}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">${position.avg_cost?.toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">${position.current_price?.toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">${position.current_value?.toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`font-medium ${position.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {position.gain_loss >= 0 ? '+' : ''}{position.gain_loss?.toFixed(2)}
                        </span>
                        <span className={`text-xs ml-1 ${position.gain_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          ({position.gain_loss_percent >= 0 ? '+' : ''}{position.gain_loss_percent?.toFixed(2)}%)
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{position.weight?.toFixed(2)}%</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center text-gray-400 text-sm">
                      No holdings yet. Click "Add Transaction" to get started!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-6 pb-0">
            <h2 className="text-lg font-semibold text-gray-900">Recent Transactions</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticker</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shares</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {transactions.length > 0 ? (
                  transactions.slice().reverse().slice(0, 10).map((trans, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 text-sm text-gray-600">{trans.purchase_date}</td>
                      <td className="px-6 py-4 text-sm font-semibold text-blue-600">{trans.ticker}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{trans.shares}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">${trans.purchase_price?.toFixed(2)}</td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        ${(trans.shares * trans.purchase_price).toFixed(2)}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-gray-400 text-sm">
                      No transactions yet
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const SummaryCard = ({ title, value, icon, format = 'number', change, color = 'blue' }) => {
  const formatValue = () => {
    if (format === 'currency') {
      return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else if (format === 'percent') {
      return `${(value * 100).toFixed(2)}%`;
    }
    return value;
  };

  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600'
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{title}</span>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-semibold text-gray-900">{formatValue()}</div>
      {change !== undefined && (
        <div className={`text-xs mt-2 font-medium ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {change >= 0 ? '↑' : '↓'} {Math.abs(change).toFixed(2)}%
        </div>
      )}
    </div>
  );
};

export default PortfolioDashboard;