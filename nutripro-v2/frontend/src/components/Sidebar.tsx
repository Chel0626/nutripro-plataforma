'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  HomeIcon, 
  UserGroupIcon, 
  DocumentTextIcon, 
  CakeIcon,
  CalculatorIcon,
  CalendarIcon 
} from '@heroicons/react/24/outline';

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Pacientes', href: '/pacientes', icon: UserGroupIcon },
  { name: 'Alimentos', href: '/alimentos', icon: CakeIcon },
  { name: 'Consultas', href: '/consultas', icon: CalendarIcon },
  { name: 'Calculadoras', href: '/calculadoras', icon: CalculatorIcon },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-screen w-64 flex-col bg-white shadow-lg">
      {/* Logo */}
      <div className="flex h-16 items-center justify-center border-b border-gray-200">
        <h1 className="text-xl font-bold text-primary-600">NutriPro V2</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-4 py-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-primary-500' : 'text-gray-400'}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* User info placeholder */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center">
            <span className="text-white text-sm font-medium">N</span>
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-700">Nutricionista</p>
            <p className="text-xs text-gray-500">nutri@nutripro.com</p>
          </div>
        </div>
      </div>
    </div>
  );
}