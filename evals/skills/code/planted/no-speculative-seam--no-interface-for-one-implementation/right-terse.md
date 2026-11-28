One class, `LateFeePolicy`, and no `FeeCalculator` interface: there is one implementation and no fake, so the interface adds a layer and hides nothing. Add it when a second implementation exists.
