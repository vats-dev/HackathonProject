import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Check } from "lucide-react";

const STEPS = [
  {
    id: 1,
    heading: "What are you looking to improve?",
    subtext: "We'll use this to personalize your plan.",
    options: [
      { id: "hair", emoji: "🌿", label: "Hair & Scalp Health", desc: "Thinning, shedding, or growth" },
      { id: "skin", emoji: "✨", label: "Skin & Radiance", desc: "Glow, texture, breakouts" },
      { id: "stress", emoji: "🧘", label: "Stress & Mood", desc: "Calm, focus, and clarity" },
      { id: "sleep", emoji: "🌙", label: "Sleep Quality", desc: "Deeper, more restorative rest" },
    ],
  },
  {
    id: 2,
    heading: "How long have you experienced this?",
    subtext: "Duration helps us calibrate your starting plan.",
    options: [
      { id: "recent", emoji: "📅", label: "Just started noticing", desc: "Less than 3 months" },
      { id: "months", emoji: "🗓️", label: "Several months", desc: "3–12 months" },
      { id: "year", emoji: "⏳", label: "Over a year", desc: "12+ months" },
      { id: "always", emoji: "♾️", label: "It's always been an issue", desc: "Chronic or ongoing" },
    ],
  },
  {
    id: 3,
    heading: "What's your primary goal?",
    subtext: "Let's understand what success looks like for you.",
    options: [
      { id: "prevent", emoji: "🛡️", label: "Prevention & maintenance", desc: "Stay ahead of it" },
      { id: "restore", emoji: "🔄", label: "Restore & recover", desc: "Get back to baseline" },
      { id: "optimize", emoji: "🚀", label: "Optimize performance", desc: "Go beyond the norm" },
      { id: "explore", emoji: "🔍", label: "Just exploring", desc: "Learning what works" },
    ],
  },
];

const fadeSlide = {
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
  transition: { duration: 0.38, ease: "easeOut" },
};

export default function OnboardingCard() {
  const [step, setStep] = useState(0);
  const [selections, setSelections] = useState({});
  const [completed, setCompleted] = useState(false);

  const current = STEPS[step];
  const progress = ((step + 1) / STEPS.length) * 100;

  const select = (id) => {
    setSelections((prev) => ({ ...prev, [current.id]: id }));
  };

  const next = () => {
    if (step < STEPS.length - 1) {
      setStep((s) => s + 1);
    } else {
      setCompleted(true);
    }
  };

  const canContinue = !!selections[current?.id];

  if (completed) {
    return (
      <motion.div
        className="bg-surface rounded-4xl shadow-elevated p-12 text-center max-w-lg mx-auto"
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <div className="w-16 h-16 rounded-full bg-primary-muted flex items-center justify-center mx-auto mb-6">
          <Check className="w-7 h-7 text-primary" strokeWidth={2} />
        </div>
        <h2 className="font-serif text-3xl text-text-main mb-3">Your plan is ready.</h2>
        <p className="text-text-muted font-sans text-sm leading-relaxed mb-8">
          Based on your answers, we've curated a personalized wellness protocol just for you.
        </p>
        <button className="btn-primary w-full justify-center">View My Protocol</button>
      </motion.div>
    );
  }

  return (
    <div className="bg-surface rounded-4xl shadow-elevated overflow-hidden max-w-lg mx-auto">
      {/* Progress bar */}
      <div className="h-1 bg-border-light">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.45, ease: "easeOut" }}
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          {...fadeSlide}
          className="p-10"
        >
          {/* Step counter */}
          <p className="section-label mb-6">
            Step {step + 1} of {STEPS.length}
          </p>

          {/* Heading */}
          <h2 className="font-serif text-[1.9rem] leading-tight text-text-main mb-2 text-balance">
            {current.heading}
          </h2>
          <p className="text-text-muted text-sm font-sans mb-8 leading-relaxed">
            {current.subtext}
          </p>

          {/* Options */}
          <div className="space-y-3 mb-8">
            {current.options.map((opt) => {
              const isSelected = selections[current.id] === opt.id;
              return (
                <motion.button
                  key={opt.id}
                  onClick={() => select(opt.id)}
                  className={`option-card ${isSelected ? "selected" : ""}`}
                  whileTap={{ scale: 0.99 }}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-2xl leading-none">{opt.emoji}</span>
                    <div className="flex-1 text-left">
                      <div className="font-medium text-text-main text-sm">{opt.label}</div>
                      <div className="text-text-muted text-xs mt-0.5">{opt.desc}</div>
                    </div>
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all duration-200
                        ${isSelected ? "border-primary bg-primary" : "border-border"}`}
                    >
                      {isSelected && <Check className="w-2.5 h-2.5 text-white" strokeWidth={3} />}
                    </div>
                  </div>
                </motion.button>
              );
            })}
          </div>

          {/* CTA */}
          <button
            onClick={next}
            disabled={!canContinue}
            className={`w-full py-4 rounded-full font-sans font-medium text-sm tracking-wide transition-all duration-300
              ${canContinue
                ? "bg-primary text-white hover:bg-primary-light hover:shadow-elevated"
                : "bg-border-light text-text-muted cursor-not-allowed"
              }`}
          >
            {step === STEPS.length - 1 ? "See My Plan" : "Continue"}
          </button>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
