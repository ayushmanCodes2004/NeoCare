export default function Spinner({ lg }) {
  const size = lg ? 'h-10 w-10 border-[3px]' : 'h-5 w-5 border-2';
  return (
    <div 
      className={`${size} animate-spin rounded-full border-teal-500 border-t-transparent`} 
    />
  );
}
