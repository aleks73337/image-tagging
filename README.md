## Hashtag assistant tool.
<img src="https://user-images.githubusercontent.com/23703391/111377893-41224e00-86b2-11eb-959f-aef144dacee3.png" width="196" height="196" />

### Overview
Hashtag assistant tool designed to reduce photo publishing time. Once you upload a photo to the social network, it will suggest you the hashtag list, basing on media content and your preferences.

### MockUp
![MockUp](https://user-images.githubusercontent.com/23703391/111376788-f6540680-86b0-11eb-89c5-93c259457454.png)

### Planning results
* Dataset
  * todo: Provide cosidered ways to gather DS, add estimation.
* Model
  * todo: Provide cosidered ways to predict hashtags, add estimation.
* User expirience
  * todo: Provide cosidered ways product application, add estimation.

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
* Can be implemented as an offline app, which provides a list of hashtags by giving an image path.
* SG: Make a Chrome extension.

### Responsibilities
* Dataset parsing - Alexey
* Model - Alexander
* GUI - Boris
