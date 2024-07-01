
import Nav from "./components/Nav";
import Main from "./components/layout/Content/Content";
import Footer from "./components/layout/Footer/Footer";




export default function Home() {
  return (
    <main className="w-full flex flex-col items-center justify-between min-h-screen ">
      <Nav/>
      <Main />
      <Footer />
    </main>
  );
}
