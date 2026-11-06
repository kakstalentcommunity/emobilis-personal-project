import React from 'react';
export function Loader(){return <div className="spinner" role="status" aria-label="Loading"/>;}
export function Skeleton({count=3}){return <div className="skeleton-list">{Array.from({length:count},(_,i)=><div className="skeleton" key={i}/>)}</div>;}
export function EmptyState({children='No activity yet.'}){return <div className="empty-box">{children}</div>;}
export function ErrorMessage({message,retry}){return <div className="error-box" role="alert"><p>{message}</p><button className="button button-outline" onClick={retry}>Retry</button></div>;}
export function StatusBadge({status}){return <span className={`badge ${['ready','served','closed'].includes(status)?'complete':''}`}>{status.replace('_',' ')}</span>;}
