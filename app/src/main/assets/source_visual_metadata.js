/* NK QBank source-visual contract (V11)
 * Visuals are optional and never inferred from question numbers.
 * type: source-pdf | future visual types
 * source: bundled PDF asset name
 * page: 1-based PDF page
 * crop: optional source-PDF coordinates in PDF points {left,top,right,bottom}
 * fit: contain | width | native
 */
window.SOURCE_VISUAL_SCHEMA = {
  version: 1,
  question: { visual: null },
  option: { visual: null }
};
