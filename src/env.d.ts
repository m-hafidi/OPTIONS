/** CSS Modules are typed as a plain class-name map until a framework (Vite/Next) provides richer types. */
declare module "*.module.css" {
  const classes: { readonly [key: string]: string };
  export default classes;
}
