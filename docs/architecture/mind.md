# Transparent Funding of Git Based Projects

## What Could Go Wrong?

### Human

 * Automated Funding will disrupt the behavior of the contributors.

 This problem can't be solved with a technical Solution. Spreading
 money based on git commit behavior will affect the behavior of people
 and it will raise fraud and abuse of the system. This behavior can't
 possibly be predicted in all its detail. Therefore it is extremely
 important that individual projects can tweak all the time their
 spending behavior based on their experience with behavior shift and
 abuse.

 The money spreading behavior should be simple and easy to understand
 for every initial project that starts using OpenSelery for their OS
 project, so that also fraud and abuse remains understandable by the
 project maintainers. They can then counter the Fraud with custom
 tweaks that they still understand but won't make the system more
 complicated for users in very different domains and fraud behavior.

 The solution that we provide is an interface programmable by the user
 where he can use different metrics (implemented by us) to tweak the
 money distribution to their specific needs and experience.

 <openselery-funding-distribution-function.py>

### Technical

 * Why is funding probability split instead of spliting the funding
   directly into micropayments?

 Each transaction has a transaction cost in coinbase. When
 transactions are not split, the losses towards coinbase are reduced
 to a minimum. The price for this is that there is the probability for
 unfair payment.

 * E-mail spamming from Coinbase.
 * Theft of Coinbase credit.
 * Single point of failure: Coinbase

 In the Longrun there should be more payment options that coinbase
 alone. We tested in the Paypal sandbox, but for production it
 enforces a commercial license, and we don't want to push our users
 into obtaining such a license.

 * Abuse of collected user data.
