import React, { useState } from 'react';
import { EntityItem, EntityType } from '../types/contract';
import {
  User,
  Building2,
  Calendar,
  DollarSign,
  MapPin,
  Scale,
  Clock,
  RefreshCw,
  CreditCard,
  Filter,
} from 'lucide-react';

interface EntityViewerProps {
  entities: EntityItem[];
}

export const EntityViewer: React.FC<EntityViewerProps> = ({ entities }) => {
  const [selectedType, setSelectedType] = useState<string>('ALL');

  const typeConfig: Record<
    EntityType,
    { icon: React.FC<{ className?: string }>; color: string; bg: string }
  > = {
    Person: { icon: User, color: 'text-sky-400', bg: 'bg-sky-500/10 border-sky-500/20' },
    Organization: {
      icon: Building2,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10 border-indigo-500/20',
    },
    Date: { icon: Calendar, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
    'Monetary Value': {
      icon: DollarSign,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
    },
    Location: { icon: MapPin, color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/20' },
    Jurisdiction: { icon: Scale, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
    'Contract Duration': {
      icon: Clock,
      color: 'text-teal-400',
      bg: 'bg-teal-500/10 border-teal-500/20',
    },
    'Renewal Date': {
      icon: RefreshCw,
      color: 'text-orange-400',
      bg: 'bg-orange-500/10 border-orange-500/20',
    },
    'Payment Term': {
      icon: CreditCard,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10 border-blue-500/20',
    },
  };

  const entityTypes = Array.from(new Set(entities.map((e) => e.entity_type)));

  const filtered =
    selectedType === 'ALL'
      ? entities
      : entities.filter((e) => e.entity_type === selectedType);

  return (
    <div className="space-y-4">
      {/* Category Pills */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <button
          onClick={() => setSelectedType('ALL')}
          className={`text-xs px-3 py-1 rounded-lg border font-medium transition-colors ${
            selectedType === 'ALL'
              ? 'bg-indigo-600 border-indigo-500 text-white shadow-xs'
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
          }`}
        >
          All ({entities.length})
        </button>
        {entityTypes.map((type) => {
          const cfg = typeConfig[type] || typeConfig['Organization'];
          const count = entities.filter((e) => e.entity_type === type).length;
          return (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`text-xs px-3 py-1 rounded-lg border font-medium transition-colors flex items-center gap-1.5 ${
                selectedType === type
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-xs'
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <cfg.icon className={`w-3 h-3 ${cfg.color}`} />
              <span>
                {type} ({count})
              </span>
            </button>
          );
        })}
      </div>

      {/* Grid of entities */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {filtered.map((item) => {
          const cfg = typeConfig[item.entity_type] || typeConfig['Organization'];
          const Icon = cfg.icon;
          return (
            <div
              key={item.id}
              className={`p-3 rounded-xl border ${cfg.bg} flex items-start gap-2.5 hover:scale-[1.01] transition-transform`}
            >
              <div className={`p-1.5 rounded-lg bg-slate-950/80 ${cfg.color} shrink-0 mt-0.5`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-1 mb-0.5">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                    {item.entity_type}
                  </span>
                  <span className="text-[10px] text-slate-500">P. {item.page_number}</span>
                </div>
                <div className="text-xs font-semibold text-slate-200 break-words">
                  {item.text}
                </div>
                {item.context && (
                  <p className="text-[11px] text-slate-400 mt-1 line-clamp-1 italic font-serif">
                    "{item.context}"
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
