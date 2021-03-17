## Hashtag assistant tool.
<img src="https://user-images.githubusercontent.com/23703391/111377893-41224e00-86b2-11eb-959f-aef144dacee3.png" width="196" height="196" />

### Overview
Hashtag assistant tool designed to reduce photo publishing time. Once you upload a photo to the social network, it will suggest you the hashtag list, basing on media content and your preferences.

### MockUp
![MockUp](https://user-images.githubusercontent.com/23703391/111376788-f6540680-86b0-11eb-89c5-93c259457454.png)

### Planning results
* Dataset
  * 1st way: Parse instagramm hashtag search results.
    * (-) Contains a lot of unrelated data.
    * (-) List of hashtags is limited.
  * 2nd way: Parse parler themes.
    * (+) Good quality content.
    * (-) Not the same as social network.
  * 3rd way. Parse instagram people profiles.
    * (+) Better quality content then in case 1.
    * (+) Can be pesonalized for customer.
    * (-) Have to define proper list of peoples to parse.
    * (-+) Model will be person-specific.
* Model
  * Single, multi-layered perceptron. With classes probabilities as output.
  * Backbone
  * Feature extractor + k-means.
* User expirience
  * Simple offline app.
    * (+) Easier to implement.
    * (-) Harder to productize.
  * Browser extension.
    * (+) Easier to productize.
    * (-) Harder to implement.

### Technical requirements
#### Dataset
* Single row in the dataset should contain.
  * Link to the image
  * List of tags in the original order.
* Should be in `json` or `csv` format.
#### Model
* Gets image as a `numpy` array on input.
* Returns list of hashtags with probabilities.
  * ```[ { "Hashtag#1" : 0.2 }, { "Hashtag#2" : 0.3 }, { "Hashtag#3" : 0.5 } ]```
#### Prototype
* Can be implemented as an offline app.
  * Provides a list of selectable hashtags by giving an image path.
  * Have a button to copy all selected at once.
* SG: Make a Chrome extension.

### Responsibilities
* Dataset parsing - Alexey
* Model - Alexander
* GUI - Boris
