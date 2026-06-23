import { BrowserRouter, Routes, Route } from "react-router-dom";

import StarField from "./components/StarField";
import Navbar from "./components/Navbar";

import Home from "./pages/Home";
import Features from "./pages/Features";
import Pricing from "./pages/Pricing";
import About from "./pages/About";
import Blog from "./pages/Blog";
import Contact from "./pages/Contact";
import BlogDetails from "./pages/BlogDetails";

import ChatApp from "./components/ChatApp";

export default function App() {
  return (
    <BrowserRouter>

      <StarField />

      <Navbar />

      <Routes>

        <Route path="/" element={<Home />} />

        <Route
          path="/features"
          element={<Features />}
        />

        <Route
          path="/pricing"
          element={<Pricing />}
        />

        <Route
          path="/about"
          element={<About />}
        />

        <Route
          path="/blog"
          element={<Blog />}
        />

        <Route
          path="/blog/:id"
          element={<BlogDetails />}
        />

        <Route
          path="/contact"
          element={<Contact />}
        />

        <Route
          path="/chat"
          element={<ChatApp />}
        />

      </Routes>

    </BrowserRouter>
  );
}