import React, { useEffect, useState } from "react";
import Navbar from "../components/NavBar";
import Sidebar from "../components/SideBar";

export default function LiveFeed() {
  const [images, setImages] = useState([]);

  useEffect(() => {
    let mounted = true;

    async function fetchImages() {
      try {
        const res = await fetch("http://localhost:3000/images/annotated");
        const files = await res.json();
        if (!mounted) return;
        setImages(files);
      } catch (err) {
        console.error("Failed to fetch annotated images", err);
      }
    }

    fetchImages();
    const interval = setInterval(fetchImages, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-semibold text-slate-700">Live Feed</h1>
            <div className="text-sm text-slate-400">Updated just now</div>
          </div>
          <div className="mt-4 bg-white rounded-lg border border-slate-100 h-[540px] flex flex-wrap items-center justify-center text-slate-400 overflow-auto">
            {images.length === 0 ? (
              <div>No images yet</div>
            ) : (
              images.map(filename => (
                <img
                  key={filename}
                  src={`http://localhost:3000/images/${filename}`}
                  alt={filename}
                  className="h-64 m-2 rounded shadow"
                  style={{ objectFit: "cover" }}
                />
              ))
            )}
          </div>
        </main>
      </div>
    </div>
  );
}