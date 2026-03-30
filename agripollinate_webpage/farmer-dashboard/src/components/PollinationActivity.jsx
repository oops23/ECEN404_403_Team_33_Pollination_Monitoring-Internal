import React, { useEffect, useState } from "react";
import Card from "./Card";

export default function PollinationActivity() {
  const [images, setImages] = useState([]);

  useEffect(() => {
    let mounted = true;
    async function fetchImages() {
      try {
        const res = await fetch("http://localhost:3000/images/lidar");
        if (!res.ok) throw new Error("Network response was not ok");
        const files = await res.json();
        if (mounted) setImages(files);
      } catch (err) {
        console.error("Failed to fetch images", err);
      }
    }
    fetchImages();
    const interval = setInterval(fetchImages, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const latest = images[0];

  return (
    <Card className="col-span-1 row-span-1 bg-white border-2 border-blue-200 rounded-lg shadow-lg p-6">
      <div className="bg-slate-200 h-64 w-full rounded-lg flex justify-center items-center text-gray-400 overflow-hidden">
        {latest ? (
          <img
            key={latest.filename}
            src={`http://localhost:3000/images/${latest.filename}`}
            alt={latest.filename}
            className="h-64px w-full rounded shadow cursor-pointer"
            style={{ objectFit: "cover"}}
          />
        ) : (
          <div>No LIDAR images yet</div>
        )}
      </div>
    </Card>
  );
}