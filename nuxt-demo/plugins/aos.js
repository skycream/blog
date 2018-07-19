import AOS from "aos";

export default ({ app }) => {
  app.AOS = new AOS.init({ disable: "phone" });
};
