import React, { useState } from 'react';
import { Check, X, Crown, Zap, Building2, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

const PricingPage = ({ session, onUpgrade, onClose }) => {
    const [billingCycle, setBillingCycle] = useState('monthly');

    const plans = [
        {
            tier: 'free',
            name: 'Free',
            icon: Sparkles,
            price: 0,
            description: 'Perfect for trying out the platform',
            features: [
                { text: '5 scans per month', included: true },
                { text: 'Basic security checks', included: true },
                { text: 'Limited findings (3 max)', included: true },
                { text: 'PDF downloads', included: false },
                { text: 'Selenium scanning', included: false },
                { text: 'Code fix snippets', included: false },
                { text: 'Automated scans', included: false },
                { text: 'API access', included: false },
            ],
            cta: 'Current Plan',
            popular: false,
            color: 'slate'
        },
        {
            tier: 'basic',
            name: 'Basic',
            icon: Zap,
            price: 29,
            description: 'Great for small teams and startups',
            features: [
                { text: '50 scans per month', included: true },
                { text: 'All security checks', included: true },
                { text: 'Unlimited findings', included: true },
                { text: 'PDF downloads', included: true },
                { text: 'Selenium scanning', included: true },
                { text: 'Compliance mapping', included: true },
                { text: 'Code fix snippets', included: false },
                { text: 'Automated scans', included: false },
            ],
            cta: 'Upgrade to Basic',
            popular: true,
            color: 'cyan'
        },
        {
            tier: 'professional',
            name: 'Professional',
            icon: Crown,
            price: 99,
            description: 'Perfect for growing businesses',
            features: [
                { text: '200 scans per month', included: true },
                { text: 'All security checks', included: true },
                { text: 'Unlimited findings', included: true },
                { text: 'PDF downloads', included: true },
                { text: 'Selenium scanning', included: true },
                { text: 'Code fix snippets', included: true },
                { text: '24/7 automated scans', included: true },
                { text: 'API access', included: true },
            ],
            cta: 'Upgrade to Pro',
            popular: false,
            color: 'purple'
        },
        {
            tier: 'enterprise',
            name: 'Enterprise',
            icon: Building2,
            price: 299,
            description: 'For large organizations',
            features: [
                { text: 'Unlimited scans', included: true },
                { text: 'All security checks', included: true },
                { text: 'Unlimited findings', included: true },
                { text: 'PDF downloads', included: true },
                { text: 'Custom branding', included: true },
                { text: 'Priority support', included: true },
                { text: 'Dedicated account manager', included: true },
                { text: 'SLA guarantees', included: true },
            ],
            cta: 'Contact Sales',
            popular: false,
            color: 'amber'
        }
    ];

    const getColorClasses = (color, type = 'bg') => {
        const colors = {
            slate: {
                bg: 'bg-slate-500',
                border: 'border-slate-500',
                text: 'text-slate-500',
                bgLight: 'bg-slate-500/10',
                hover: 'hover:bg-slate-600'
            },
            cyan: {
                bg: 'bg-cyan-500',
                border: 'border-cyan-500',
                text: 'text-cyan-500',
                bgLight: 'bg-cyan-500/10',
                hover: 'hover:bg-cyan-600'
            },
            purple: {
                bg: 'bg-purple-500',
                border: 'border-purple-500',
                text: 'text-purple-500',
                bgLight: 'bg-purple-500/10',
                hover: 'hover:bg-purple-600'
            },
            amber: {
                bg: 'bg-amber-500',
                border: 'border-amber-500',
                text: 'text-amber-500',
                bgLight: 'bg-amber-500/10',
                hover: 'hover:bg-amber-600'
            }
        };
        return colors[color][type];
    };

    return (
        <div className="min-h-screen bg-[#0A0F1C] text-white py-20 px-4">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="text-center mb-16">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-sm font-mono tracking-widest uppercase mb-6"
                    >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Pricing Plans
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl md:text-7xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-cyan-100 to-cyan-400 pb-2 mb-6"
                    >
                        Choose Your Plan
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="text-xl text-slate-400 max-w-2xl mx-auto"
                    >
                        Unlock powerful security scanning features with our flexible pricing options
                    </motion.p>

                    {/* Billing Toggle */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="flex items-center justify-center gap-4 mt-8"
                    >
                        <span className={`text-sm font-semibold ${billingCycle === 'monthly' ? 'text-white' : 'text-slate-500'}`}>
                            Monthly
                        </span>
                        <button
                            onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
                            className="relative w-14 h-7 bg-slate-700 rounded-full transition-colors hover:bg-slate-600"
                        >
                            <div className={`absolute top-1 left-1 w-5 h-5 bg-cyan-500 rounded-full transition-transform ${billingCycle === 'yearly' ? 'translate-x-7' : ''}`} />
                        </button>
                        <span className={`text-sm font-semibold ${billingCycle === 'yearly' ? 'text-white' : 'text-slate-500'}`}>
                            Yearly
                            <span className="ml-2 text-xs text-cyan-400">(Save 20%)</span>
                        </span>
                    </motion.div>
                </div>

                {/* Pricing Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    {plans.map((plan, index) => {
                        const Icon = plan.icon;
                        const yearlyPrice = Math.round(plan.price * 12 * 0.8);
                        const displayPrice = billingCycle === 'yearly' ? yearlyPrice : plan.price;

                        return (
                            <motion.div
                                key={plan.tier}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 * index }}
                                className={`relative bg-slate-900/40 border ${plan.popular ? 'border-cyan-500 shadow-lg shadow-cyan-500/20' : 'border-slate-800'} rounded-2xl p-8 hover:border-cyan-500/50 transition-all group`}
                            >
                                {/* Popular Badge */}
                                {plan.popular && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full text-xs font-bold text-black">
                                        MOST POPULAR
                                    </div>
                                )}

                                {/* Icon */}
                                <div className={`w-12 h-12 rounded-xl ${getColorClasses(plan.color, 'bgLight')} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                                    <Icon className={`w-6 h-6 ${getColorClasses(plan.color, 'text')}`} />
                                </div>

                                {/* Plan Name */}
                                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                                <p className="text-slate-400 text-sm mb-6">{plan.description}</p>

                                {/* Price */}
                                <div className="mb-6">
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-5xl font-black">${displayPrice}</span>
                                        {plan.price > 0 && (
                                            <span className="text-slate-500 text-sm">
                                                /{billingCycle === 'yearly' ? 'year' : 'month'}
                                            </span>
                                        )}
                                    </div>
                                    {billingCycle === 'yearly' && plan.price > 0 && (
                                        <p className="text-xs text-cyan-400 mt-2">
                                            ${Math.round(yearlyPrice / 12)}/month billed annually
                                        </p>
                                    )}
                                </div>

                                {/* CTA Button */}
                                <button
                                    onClick={() => onUpgrade(plan.tier)}
                                    disabled={!session && plan.tier !== 'free'}
                                    className={`w-full py-3 rounded-xl font-bold transition-all mb-6 ${plan.popular
                                            ? `${getColorClasses(plan.color, 'bg')} text-black ${getColorClasses(plan.color, 'hover')}`
                                            : `bg-slate-800 text-white hover:bg-slate-700 ${!session && plan.tier !== 'free' ? 'opacity-50 cursor-not-allowed' : ''}`
                                        }`}
                                >
                                    {!session && plan.tier !== 'free' ? 'Sign In Required' : plan.cta}
                                </button>

                                {/* Features List */}
                                <ul className="space-y-3">
                                    {plan.features.map((feature, idx) => (
                                        <li key={idx} className="flex items-start gap-3 text-sm">
                                            {feature.included ? (
                                                <Check className={`w-5 h-5 ${getColorClasses(plan.color, 'text')} flex-shrink-0 mt-0.5`} />
                                            ) : (
                                                <X className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" />
                                            )}
                                            <span className={feature.included ? 'text-slate-300' : 'text-slate-600'}>
                                                {feature.text}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </motion.div>
                        );
                    })}
                </div>

                {/* Feature Comparison Table */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8"
                >
                    <h2 className="text-2xl font-bold mb-6 text-center">Feature Comparison</h2>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-800">
                                    <th className="text-left py-4 px-4 text-slate-400 font-semibold">Feature</th>
                                    <th className="text-center py-4 px-4 text-slate-400 font-semibold">Free</th>
                                    <th className="text-center py-4 px-4 text-cyan-400 font-semibold">Basic</th>
                                    <th className="text-center py-4 px-4 text-purple-400 font-semibold">Professional</th>
                                    <th className="text-center py-4 px-4 text-amber-400 font-semibold">Enterprise</th>
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    { name: 'Scans per month', values: ['5', '50', '200', 'Unlimited'] },
                                    { name: 'PDF Downloads', values: [false, true, true, true] },
                                    { name: 'Selenium Scanning', values: [false, true, true, true] },
                                    { name: 'Code Fix Snippets', values: [false, false, true, true] },
                                    { name: 'Automated Scans', values: [false, false, true, true] },
                                    { name: 'API Access', values: [false, false, true, true] },
                                    { name: 'Priority Support', values: [false, false, false, true] },
                                    { name: 'Custom Branding', values: [false, false, false, true] },
                                ].map((row, idx) => (
                                    <tr key={idx} className="border-b border-slate-800/50">
                                        <td className="py-4 px-4 text-slate-300">{row.name}</td>
                                        {row.values.map((value, colIdx) => (
                                            <td key={colIdx} className="py-4 px-4 text-center">
                                                {typeof value === 'boolean' ? (
                                                    value ? (
                                                        <Check className="w-5 h-5 text-green-500 mx-auto" />
                                                    ) : (
                                                        <X className="w-5 h-5 text-slate-600 mx-auto" />
                                                    )
                                                ) : (
                                                    <span className="text-slate-300">{value}</span>
                                                )}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </motion.div>

                {/* FAQ Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="mt-16 text-center"
                >
                    <h2 className="text-3xl font-bold mb-8">Frequently Asked Questions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                        {[
                            {
                                q: 'Can I change plans anytime?',
                                a: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.'
                            },
                            {
                                q: 'What payment methods do you accept?',
                                a: 'We accept all major credit cards, debit cards, and PayPal through Stripe.'
                            },
                            {
                                q: 'Is there a free trial?',
                                a: 'The Free plan is available forever. Upgrade anytime to access premium features.'
                            },
                            {
                                q: 'Do you offer refunds?',
                                a: '30-day money-back guarantee on all paid plans. No questions asked.'
                            }
                        ].map((faq, idx) => (
                            <div key={idx} className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 text-left">
                                <h3 className="font-bold text-lg mb-2">{faq.q}</h3>
                                <p className="text-slate-400 text-sm">{faq.a}</p>
                            </div>
                        ))}
                    </div>
                </motion.div>
            </div>
        </div>
    );
};

export default PricingPage;
