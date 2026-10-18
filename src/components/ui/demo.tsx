"use client";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function TabsDemo() {
  return (
    <Tabs defaultValue="black-scholes" className="w-full max-w-md">
      <TabsList>
        <TabsTrigger value="black-scholes">Black-Scholes</TabsTrigger>
        <TabsTrigger value="monte-carlo">Monte Carlo</TabsTrigger>
        <TabsTrigger value="binomial">Binomial Tree</TabsTrigger>
      </TabsList>
      <TabsContent value="black-scholes">
        Closed-form solution for European call and put prices, derived from the
        Greeks' d1 and d2 terms. No simulation needed — instant, exact results.
      </TabsContent>
      <TabsContent value="monte-carlo">
        Simulates thousands of random price paths to the expiry date and averages
        the discounted payoff. Shows the distribution of possible outcomes.
      </TabsContent>
      <TabsContent value="binomial">
        Builds a recombining price tree over discrete time steps, working backward
        from expiry to today. Visualises how the option value converges.
      </TabsContent>
    </Tabs>
  );
}
