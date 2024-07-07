
import Header from "./components/layout/Header/Header";
import Main from "./components/layout/Main/Main";
import Footer from "./components/layout/Footer/Footer";




export default function Home() {
  return (
    <div className="w-full bg-bg flex flex-col items-center justify-between min-h-screen ">
      <Header/>
      <Main />
      <Footer />
    </div>
  );
}
