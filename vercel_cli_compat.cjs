// Work around Vercel OAuth's ASCII User-Agent requirement for Korean hostnames.
// This affects only the current Node process, never the Windows device name.
const os=require('node:os');
if([...os.hostname()].some(c=>c.codePointAt(0)>127)){
  os.hostname=()=> 'MathQuest';
  require('node:module').syncBuiltinESMExports();
}
