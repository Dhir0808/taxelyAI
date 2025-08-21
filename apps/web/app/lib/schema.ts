export type CompanyInput = {
  companyName?: string;
  companyNumber?: string;
  accountingYear: number;
  revenueGBP: number;
  expensesGBP: number;
  rAndDSpendGBP?: number;
  patentRevenueGBP?: number;
  capexGBP?: number;
  applyCredits?: boolean;
};
